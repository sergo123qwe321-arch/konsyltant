#!/usr/bin/env python3
"""
scripts/admin/sanitize_production_db.py — санация боевой базы
(Этап 7, шаг 7.2б; Этап 8, шаг 8.2 — поддержка PostgreSQL).

Поддерживает обе СУБД через единый вход `database.get_connection()`:
  * SQLite (локально: konsyltant.db / SQLITE_DB_PATH):
      - `PRAGMA foreign_keys = ON`;
      - явная транзакция `BEGIN IMMEDIATE` ... `COMMIT`/`ROLLBACK`;
      - `VACUUM` после коммита (дефрагментация файла);
      - бэкап = копия файла `konsyltant.db.backup_<timestamp>` (shutil.copy2).
  * PostgreSQL (прод, контейнер с `DATABASE_URL=postgresql://...`):
      - штатная транзакция `COMMIT`/`ROLLBACK` (прагма и VACUUM не применяются);
      - бэкап = `pg_dump --format=custom` в `backups/konsyltant_pg_<timestamp>.dump`.

Правила очистки (одинаковы для обеих СУБД, утверждены Архитектором в шаге 8.6):
  - удаление из `doctors` всего, что не входит в утвержденный Allowlist
    (`DOC-KSENIA-001`, `DOC-SVETLANA-001`) — ровно 2 специалиста;
  - `patient_share_grants`: удаляются только «висячие» записи, чей
    `patient_folder_id` не входит в белый список папок реальных Родителей
    (активные гранты семей сохраняются); `doctor_notes`,
    `doctor_chat_history`, `patient_analyses_documents` — по doctor_id
    вне Allowlist или «висячие» (NULL);
  - `patient_access`: удаляются тестовые и служебные учетки; белый список:
    админы `admin`/`svetlana`, папки реальных Родителей из
    `KEEP_PATIENT_FOLDERS`; строки роли `DOCTOR` не сохраняются;
  - идемпотентный фикс каталога Светланы `admin_vault` -> `admin_vault_svetlana`.

Все списки (Allowlist, keep-list) подставляются в SQL строковыми литералами —
синтаксис `IN (...)`/`NOT IN (...)` идентично валиден в SQLite и PostgreSQL.

По умолчанию — dry-run (только статистика, без изменений и без бэкапа).
Фактическое выполнение: `--apply`.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import database  # noqa: E402  — строго после выставления sys.path

# Утвержденный Allowlist специалистов (Этап 8, шаг 8.6): ровно 2 специалиста
ALLOWLIST_LICENSES = ("DOC-KSENIA-001", "DOC-SVETLANA-001")

# Собственный каталог администратора Светланы (устранение коллизии admin_vault)
SVETLANA_LOGIN = "svetlana"
SVETLANA_VAULT = "admin_vault_svetlana"

# Учетные записи, которые сохраняются в patient_access
KEEP_ADMIN_TOKENS = ("admin", "svetlana")
# Этап 8.6: роли DOCTOR в patient_access не сохраняются (специалисты — в doctors)
KEEP_DOCTOR_TOKENS = ()

# Белый список папок реальных Родителей и сервисной папки (шаг 8.6, точные
# литералы получены из боевой PostgreSQL, включая двойные пробелы)
KEEP_PATIENT_FOLDERS = (
    "disk:/Дюзгёрен Арон Альп",
    "disk:/Диагностика Пациент",
    "disk:/Змиенко",
    "disk:/Кешишьян Тигран Левонович",
    "disk:/Кирисик Михаэль Саакович",
    "disk:/Малышкин Даня",
    "disk:/Прияцелюк Матвей Сергеевич",
    "disk:/Ропаев Степан Артурович",
    "disk:/Харламов Владимир Станиславович",
    "disk:/Эмексузян Альберт Саакович",
    "disk:/Якушева Маргарита  Витпльевна",
    "disk:/Змиенко Ионна Владиславовна",
    "disk:/Дюзгёрен  Арон  Альп.",
)

CHILD_TABLES = (
    "patient_share_grants",
    "doctor_notes",
    "doctor_chat_history",
    "patient_analyses_documents",
)


def sql_in(values) -> str:
    """Список строковых литералов для IN/NOT IN (валидно в SQLite и PostgreSQL)."""
    return ", ".join("'" + str(v).replace("'", "''") + "'" for v in values)


ALLOWLIST_SQL = sql_in(ALLOWLIST_LICENSES)
KEEP_PATIENT_FOLDERS_SQL = sql_in(KEEP_PATIENT_FOLDERS)

CHILD_DELETE_SQL = (
    "DELETE FROM {table} WHERE doctor_id IS NULL "
    f"OR doctor_id NOT IN (SELECT id FROM doctors WHERE license_number IN ({ALLOWLIST_SQL}))"
)
CHILD_COUNT_SQL = (
    "SELECT COUNT(*) FROM {table} WHERE doctor_id IS NULL "
    f"OR doctor_id NOT IN (SELECT id FROM doctors WHERE license_number IN ({ALLOWLIST_SQL}))"
)

# Гранты (шаг 8.6): удаляются только «висячие» записи, чья папка не входит
# в белый список реальных Родителей; активные гранты семей сохраняются.
_GRANTS_WHERE = (
    "patient_folder_id IS NULL "
    f"OR patient_folder_id NOT IN ({KEEP_PATIENT_FOLDERS_SQL})"
)
GRANTS_DELETE_SQL = f"DELETE FROM patient_share_grants WHERE {_GRANTS_WHERE}"
GRANTS_COUNT_SQL = f"SELECT COUNT(*) FROM patient_share_grants WHERE {_GRANTS_WHERE}"

_DOCTOR_CLAUSE = (
    "(role = 'DOCTOR' AND access_token NOT IN (" + sql_in(KEEP_DOCTOR_TOKENS) + "))"
    if KEEP_DOCTOR_TOKENS
    else "(role = 'DOCTOR')"
)
PATIENT_ACCESS_WHERE = (
    "((role = 'ADMIN' AND access_token NOT IN (" + sql_in(KEEP_ADMIN_TOKENS) + ")) "
    "OR " + _DOCTOR_CLAUSE + " "
    "OR (role = 'PATIENT' AND COALESCE(gdrive_folder_id, '') NOT IN ("
    + KEEP_PATIENT_FOLDERS_SQL + ")))"
)
PATIENT_ACCESS_DELETE_SQL = "DELETE FROM patient_access WHERE " + PATIENT_ACCESS_WHERE
PATIENT_ACCESS_COUNT_SQL = "SELECT COUNT(*) FROM patient_access WHERE " + PATIENT_ACCESS_WHERE

SVETLANA_UPDATE_SQL = (
    "UPDATE patient_access SET gdrive_folder_id = ? "
    "WHERE access_token = ? AND role = 'ADMIN' AND COALESCE(gdrive_folder_id, '') <> ?"
)


def resolve_sqlite_path(cli_path: str) -> Path:
    if cli_path:
        return Path(cli_path)
    env_path = os.getenv("SQLITE_DB_PATH") or os.getenv("DB_FILE")
    if env_path:
        return Path(env_path)
    return Path(database.DB_FILE)


def make_backup(is_postgres: bool, sqlite_path: Path) -> Path:
    """Резервная копия ПЕРЕД записью: файл (SQLite) или pg_dump (PostgreSQL)."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    if is_postgres:
        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            raise RuntimeError("DATABASE_URL не задан — pg_dump невозможен.")
        out_path = PROJECT_ROOT / "backups" / f"konsyltant_pg_{timestamp}.dump"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["pg_dump", f"--dbname={db_url}", "--format=custom", f"--file={out_path}"]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise RuntimeError(
                "pg_dump не найден в PATH — на проде бэкап обязателен, прерывание."
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"pg_dump завершился с ошибкой: {(exc.stderr or '').strip()}"
            )
        return out_path
    backup_path = sqlite_path.with_name(f"{sqlite_path.name}.backup_{timestamp}")
    shutil.copy2(sqlite_path, backup_path)
    return backup_path


def collect_stats(conn) -> dict:
    cursor = conn.cursor()
    stats = {"tables": {}, "keep_doctors": [], "patient_access_breakdown": {}}

    # 1. Врачи
    database.execute_query(cursor, "SELECT COUNT(*) FROM doctors")
    total = cursor.fetchone()[0]
    database.execute_query(
        cursor,
        "SELECT id, full_name, license_number, email FROM doctors "
        f"WHERE license_number IN ({ALLOWLIST_SQL}) ORDER BY id",
    )
    keep_rows = cursor.fetchall()
    stats["keep_doctors"] = keep_rows
    stats["tables"]["doctors"] = {
        "total": total,
        "keep": len(keep_rows),
        "delete": total - len(keep_rows),
    }

    # 2. Зависимые таблицы
    for table in CHILD_TABLES:
        database.execute_query(cursor, f"SELECT COUNT(*) FROM {table}")
        table_total = cursor.fetchone()[0]
        count_sql = (
            GRANTS_COUNT_SQL
            if table == "patient_share_grants"
            else CHILD_COUNT_SQL.format(table=table)
        )
        database.execute_query(cursor, count_sql)
        to_delete = cursor.fetchone()[0]
        stats["tables"][table] = {
            "total": table_total,
            "keep": table_total - to_delete,
            "delete": to_delete,
        }

    # 3. Учетные записи
    database.execute_query(cursor, "SELECT COUNT(*) FROM patient_access")
    pa_total = cursor.fetchone()[0]
    database.execute_query(cursor, PATIENT_ACCESS_COUNT_SQL)
    pa_delete = cursor.fetchone()[0]
    stats["tables"]["patient_access"] = {
        "total": pa_total,
        "keep": pa_total - pa_delete,
        "delete": pa_delete,
    }
    for role in ("ADMIN", "DOCTOR", "PATIENT"):
        database.execute_query(
            cursor, "SELECT COUNT(*) FROM patient_access WHERE role = ?", (role,)
        )
        role_total = cursor.fetchone()[0]
        database.execute_query(
            cursor, PATIENT_ACCESS_COUNT_SQL + " AND role = ?", (role,)
        )
        role_delete = cursor.fetchone()[0]
        stats["patient_access_breakdown"][role] = {
            "total": role_total,
            "delete": role_delete,
            "keep": role_total - role_delete,
        }

    # 4. Каталог Светланы (коллизия admin_vault -> admin_vault_svetlana)
    database.execute_query(
        cursor,
        "SELECT gdrive_folder_id FROM patient_access WHERE access_token = ? AND role = 'ADMIN'",
        (SVETLANA_LOGIN,),
    )
    svetlana_folder = cursor.fetchone()
    stats["svetlana_vault"] = svetlana_folder[0] if svetlana_folder else "(нет записи)"
    stats["svetlana_vault_ok"] = stats["svetlana_vault"] == SVETLANA_VAULT
    return stats


def print_stats(stats: dict, target: str) -> None:
    print("=" * 72)
    print(f"САНАЦИЯ БАЗЫ: {target}")
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


def apply_sanitize(conn, is_postgres: bool) -> None:
    """Единая транзакция санации (COMMIT при успехе, ROLLBACK при ошибке)."""
    cursor = conn.cursor()
    if not is_postgres:
        # PRAGMA меняется только вне транзакции; далее явный BEGIN (изоляция записи)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
    try:
        # 1. Зависимые записи (до удаления врачей — явно, без надежды на каскад)
        for table in CHILD_TABLES:
            if table == "patient_share_grants":
                database.execute_query(cursor, GRANTS_DELETE_SQL)
            else:
                database.execute_query(cursor, CHILD_DELETE_SQL.format(table=table))
        # 2. Врачи вне Allowlist
        database.execute_query(
            cursor, f"DELETE FROM doctors WHERE license_number NOT IN ({ALLOWLIST_SQL})"
        )
        # 3. Тестовые учетные записи
        database.execute_query(cursor, PATIENT_ACCESS_DELETE_SQL)
        # 4. Каталог Светланы (устранение коллизии с admin_vault)
        database.execute_query(
            cursor, SVETLANA_UPDATE_SQL, (SVETLANA_VAULT, SVETLANA_LOGIN, SVETLANA_VAULT)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Санация боевой базы (SQLite/PostgreSQL), Этап 7.2б + 8.2"
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
        help="путь к файлу SQLite (только для SQLite; игнорируется при PostgreSQL)",
    )
    args = parser.parse_args()

    is_postgres = database.check_is_postgres()

    if is_postgres:
        target = "PostgreSQL (DATABASE_URL)"
        sqlite_path = None
        if args.db:
            print("[ERROR] --db применим только к SQLite; для PostgreSQL используется "
                  "DATABASE_URL окружения.")
            return 1
    else:
        if args.db:
            os.environ["SQLITE_DB_PATH"] = args.db
            os.environ["DB_FILE"] = args.db
        sqlite_path = resolve_sqlite_path(args.db)
        target = str(sqlite_path)
        if sqlite_path.name.startswith("test_"):
            print(f"[ERROR] Это тестовая база ({sqlite_path.name}) — санация запрещена. "
                  "Запускайте скрипт без переменных SQLITE_DB_PATH/DB_FILE.")
            return 1
        if not sqlite_path.exists():
            print(f"[ERROR] База не найдена: {sqlite_path}")
            return 1

    conn = database.get_connection()
    try:
        stats = collect_stats(conn)
        print_stats(stats, target)

        if not args.apply:
            print("DRY-RUN: изменения не выполнялись. Для применения: --apply")
            return 0

        try:
            backup_path = make_backup(is_postgres, sqlite_path)
        except RuntimeError as exc:
            print(f"[ERROR] Бэкап не создан, санация прервана: {exc}")
            return 1
        print(f"[BACKUP] Резервная копия создана: {backup_path}")

        apply_sanitize(conn, is_postgres)
        print("[APPLY] Транзакция санации выполнена и подтверждена.")

        if is_postgres:
            print("[VACUUM] Пропущено: для PostgreSQL дефрагментация файла не требуется "
                  "(изменения уже подтверждены COMMIT).")
        else:
            conn.execute("VACUUM")
            print("[VACUUM] Файл базы дефрагментирован.")

        after = collect_stats(conn)
        print("\nИТОГОВОЕ СОСТОЯНИЕ:")
        print_stats(after, target)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
