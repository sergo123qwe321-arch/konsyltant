#!/usr/bin/env python3
"""
scripts/admin/sanitize_production_db.py — санация боевой базы konsyltant.db
(Этап 7, шаг 7.2б).

Что делает:
  1. Авто-резервная копия `konsyltant.db.backup_<timestamp>` (shutil.copy2) ПЕРЕД записью.
  2. Единая транзакция c `PRAGMA foreign_keys = ON`:
       - удаление из `doctors` всего, что не входит в утвержденный Allowlist;
       - удаление зависимых записей (`patient_share_grants`, `doctor_notes`,
         `doctor_chat_history`, `patient_analyses_documents`) с doctor_id вне
         Allowlist или «висячих» (NULL / уже удаленные врачи);
       - удаление тестовых учеток из `patient_access` (keep-list: admin,
         svetlana, DOC-PRODUCER/PRODUCER-001), реальные записи пациентов не трогаются.
  3. `VACUUM` после коммита (дефрагментация файла).

По умолчанию — dry-run (только статистика, без изменений и без бэкапа).
Фактическое выполнение: `--apply`.
"""
import argparse
import os
import shutil
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Утвержденный Allowlist специалистов (Этап 7, шаг 7.2б)
ALLOWLIST_LICENSES = ("DOC-KSENIA-001", "DOC-PRODUCER", "PRODUCER-001")

# Собственный каталог администратора Светланы (устранение коллизии с admin_vault)
SVETLANA_LOGIN = "svetlana"
SVETLANA_VAULT = "admin_vault_svetlana"

# Учетные записи, которые сохраняются в patient_access
KEEP_ADMIN_TOKENS = ("admin", "svetlana")
KEEP_DOCTOR_TOKENS = ("producer@cmz.site", "PRODUCER-001")

# Явные тестовые артефакты среди пациентов (сгенерированы автотестами/UAT-сидами)
TEST_PATIENT_FOLDERS = ("test_folder_jwt_789", "disk:/Тестовый Пациент")
TEST_PATIENT_TOKENS = ("patient_producer_test_2026", "test_patient_token_2026")

CHILD_TABLES = (
    "patient_share_grants",
    "doctor_notes",
    "doctor_chat_history",
    "patient_analyses_documents",
)

PLACEHOLDER_DOCS = ",".join("?" * len(ALLOWLIST_LICENSES))
PLACEHOLDER_ADMINS = ",".join("?" * len(KEEP_ADMIN_TOKENS))
PLACEHOLDER_DOCTORS = ",".join("?" * len(KEEP_DOCTOR_TOKENS))
PLACEHOLDER_TEST_FOLDERS = ",".join("?" * len(TEST_PATIENT_FOLDERS))
PLACEHOLDER_TEST_TOKENS = ",".join("?" * len(TEST_PATIENT_TOKENS))

CHILD_DELETE_SQL = (
    "DELETE FROM {table} WHERE doctor_id IS NULL "
    "OR doctor_id NOT IN (SELECT id FROM doctors WHERE license_number IN ({allowlist}))"
)
PATIENT_ACCESS_WHERE = (
    "(("
    f"role = 'ADMIN' AND access_token NOT IN ({PLACEHOLDER_ADMINS})) "
    f"OR (role = 'DOCTOR' AND access_token NOT IN ({PLACEHOLDER_DOCTORS})) "
    "OR (role = 'PATIENT' AND ("
    f"gdrive_folder_id IN ({PLACEHOLDER_TEST_FOLDERS}) "
    f"OR access_token IN ({PLACEHOLDER_TEST_TOKENS}))))"
)
PATIENT_ACCESS_DELETE_SQL = "DELETE FROM patient_access WHERE " + PATIENT_ACCESS_WHERE
PATIENT_ACCESS_COUNT_SQL = "SELECT COUNT(*) FROM patient_access WHERE " + PATIENT_ACCESS_WHERE


def resolve_db_path(cli_path: str) -> Path:
    if cli_path:
        return Path(cli_path)
    env_path = os.getenv("SQLITE_DB_PATH") or os.getenv("DB_FILE")
    if env_path:
        return Path(env_path)
    return PROJECT_ROOT / "konsyltant.db"


def make_backup(db_path: Path) -> Path:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_name(f"{db_path.name}.backup_{timestamp}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def child_delete_params() -> tuple:
    return tuple(ALLOWLIST_LICENSES)


def patient_access_delete_params() -> tuple:
    return (
        *KEEP_ADMIN_TOKENS,
        *KEEP_DOCTOR_TOKENS,
        *TEST_PATIENT_FOLDERS,
        *TEST_PATIENT_TOKENS,
    )


def collect_stats(conn: sqlite3.Connection) -> dict:
    cursor = conn.cursor()
    stats = {"tables": {}, "keep_doctors": [], "patient_access_breakdown": {}}

    # 1. Врачи
    total = cursor.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    keep_rows = cursor.execute(
        "SELECT id, full_name, license_number, email FROM doctors "
        f"WHERE license_number IN ({PLACEHOLDER_DOCS}) ORDER BY id",
        tuple(ALLOWLIST_LICENSES),
    ).fetchall()
    keep_ids = [row[0] for row in keep_rows]
    stats["keep_doctors"] = keep_rows
    stats["tables"]["doctors"] = {
        "total": total,
        "keep": len(keep_rows),
        "delete": total - len(keep_rows),
    }

    # 2. Зависимые таблицы
    for table in CHILD_TABLES:
        table_total = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        to_delete = cursor.execute(
            f"SELECT COUNT(*) FROM {table} WHERE doctor_id IS NULL "
            f"OR doctor_id NOT IN (SELECT id FROM doctors WHERE license_number IN ({PLACEHOLDER_DOCS}))",
            tuple(ALLOWLIST_LICENSES),
        ).fetchone()[0]
        stats["tables"][table] = {
            "total": table_total,
            "keep": table_total - to_delete,
            "delete": to_delete,
        }

    # 3. Учетные записи
    pa_total = cursor.execute("SELECT COUNT(*) FROM patient_access").fetchone()[0]
    pa_delete = cursor.execute(
        PATIENT_ACCESS_COUNT_SQL, patient_access_delete_params()
    ).fetchone()[0]
    stats["tables"]["patient_access"] = {
        "total": pa_total,
        "keep": pa_total - pa_delete,
        "delete": pa_delete,
    }
    for role in ("ADMIN", "DOCTOR", "PATIENT"):
        role_total = cursor.execute(
            "SELECT COUNT(*) FROM patient_access WHERE role = ?", (role,)
        ).fetchone()[0]
        role_delete = cursor.execute(
            PATIENT_ACCESS_COUNT_SQL + " AND role = ?",
            (*patient_access_delete_params(), role),
        ).fetchone()[0]
        stats["patient_access_breakdown"][role] = {
            "total": role_total,
            "delete": role_delete,
            "keep": role_total - role_delete,
        }

    # 4. Каталог Светланы (коллизия admin_vault -> admin_vault_svetlana)
    svetlana_folder = cursor.execute(
        "SELECT gdrive_folder_id FROM patient_access WHERE access_token = ? AND role = 'ADMIN'",
        (SVETLANA_LOGIN,),
    ).fetchone()
    stats["svetlana_vault"] = svetlana_folder[0] if svetlana_folder else "(нет записи)"
    stats["svetlana_vault_ok"] = stats["svetlana_vault"] == SVETLANA_VAULT
    return stats


def print_stats(stats: dict, db_path: Path) -> None:
    print("=" * 72)
    print(f"САНАЦИЯ БАЗЫ: {db_path}")
    print("Allowlist специалистов:", ", ".join(ALLOWLIST_LICENSES))
    print("=" * 72)
    header = f"{'Таблица':<30}{'Было':>8}{'Удалить':>10}{'Оставить':>11}"
    print(header)
    print("-" * len(header))
    for table, info in stats["tables"].items():
        print(f"{table:<30}{info['total']:>8}{info['delete']:>10}{info['keep']:>11}")
    print("-" * len(header))
    print("Учетные записи (по ролям):")
    for role, info in stats["patient_access_breakdown"].items():
        print(f"  {role:<28}{info['total']:>5}{info['delete']:>10}{info['keep']:>11}")
    print("-" * len(header))
    print("Каталог Светланы: "
          f"{stats['svetlana_vault']} -> ожидается '{SVETLANA_VAULT}' "
          f"[{'OK' if stats['svetlana_vault_ok'] else 'ТРЕБУЕТ ИЗМЕНЕНИЯ'}]")
    print("Врачи, остающиеся в базе (Allowlist):")
    for doc_id, full_name, license_number, email in stats["keep_doctors"]:
        print(f"  id={doc_id:<5} {license_number:<18} {full_name} <{email or '-'}>")
    print("=" * 72)


def apply_sanitize(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.execute("BEGIN IMMEDIATE")
    try:
        # 1. Зависимые записи (до удаления врачей — явно, без надежды на каскад)
        for table in CHILD_TABLES:
            cursor.execute(
                CHILD_DELETE_SQL.format(table=table, allowlist=PLACEHOLDER_DOCS),
                child_delete_params(),
            )
        # 2. Врачи вне Allowlist
        cursor.execute(
            f"DELETE FROM doctors WHERE license_number NOT IN ({PLACEHOLDER_DOCS})",
            tuple(ALLOWLIST_LICENSES),
        )
        # 3. Тестовые учетные записи
        cursor.execute(
            PATIENT_ACCESS_DELETE_SQL, patient_access_delete_params()
        )
        # 4. Каталог Светланы (устранение коллизии с admin_vault)
        cursor.execute(
            "UPDATE patient_access SET gdrive_folder_id = ? "
            "WHERE access_token = ? AND role = 'ADMIN' AND COALESCE(gdrive_folder_id, '') <> ?",
            (SVETLANA_VAULT, SVETLANA_LOGIN, SVETLANA_VAULT),
        )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Санация боевой базы konsyltant.db (Этап 7, шаг 7.2б)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="фактическое выполнение (по умолчанию dry-run со статистикой)",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="путь к файлу SQLite (по умолчанию: SQLITE_DB_PATH / konsyltant.db)",
    )
    args = parser.parse_args()

    db_path = resolve_db_path(args.db)
    if not db_path.exists():
        print(f"[ERROR] База не найдена: {db_path}")
        return 1
    if db_path.name.startswith("test_"):
        print(f"[ERROR] Это тестовая база ({db_path.name}) — санация запрещена. "
              "Запускайте скрипт без переменных SQLITE_DB_PATH/DB_FILE.")
        return 1

    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        stats = collect_stats(conn)
        print_stats(stats, db_path)

        if not args.apply:
            print("DRY-RUN: изменения не выполнялись. Для применения: --apply")
            return 0

        backup_path = make_backup(db_path)
        print(f"[BACKUP] Резервная копия создана: {backup_path.name}")

        apply_sanitize(conn)
        print("[APPLY] Транзакция санации выполнена и подтверждена.")

        conn.execute("VACUUM")
        print("[VACUUM] Файл базы дефрагментирован.")

        after = collect_stats(conn)
        print("\nИТОГОВОЕ СОСТОЯНИЕ:")
        print_stats(after, db_path)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
