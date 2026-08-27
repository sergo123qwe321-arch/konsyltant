#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Подсистема автоматизированного резервного копирования и ротации дампов БД
Проект: ИИ-Консультант «Маленькая Страна» (цмз.site)
Соответствие требованиям 152-ФЗ по непрерывности и сохранности медицинских данных
=============================================================================
"""

import os
import sys
import time
import gzip
import shutil
import sqlite3
import logging
import argparse
import subprocess
import urllib.parse
from datetime import datetime
from typing import Optional, List, Dict

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Добавляем корень проекта в sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import database

logger = logging.getLogger("backup_service")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

DEFAULT_BACKUP_DIR = os.path.join(PROJECT_ROOT, "backups")
DEFAULT_RETENTION_DAYS = 7
DEFAULT_MAX_BACKUPS = 7


def get_backup_dir(custom_dir: Optional[str] = None) -> str:
    """
    Возвращает абсолютный путь к директории бэкапов и гарантирует ее существование.
    """
    target_dir = os.path.abspath(custom_dir) if custom_dir else DEFAULT_BACKUP_DIR
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def format_bytes(size_bytes: int) -> str:
    """
    Преобразует размер в байтах в человекочитаемый формат (B, KB, MB, GB).
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def get_db_config() -> dict:
    """
    Извлекает параметры подключения к базе данных из переменных окружения.
    """
    db_url = os.getenv("DATABASE_URL", "").strip()
    is_postgres = database.check_is_postgres()
    
    config = {
        "is_postgres": is_postgres,
        "host": os.getenv("POSTGRES_HOST", "db").strip() or "localhost",
        "port": int(os.getenv("POSTGRES_PORT", "5432").strip() or "5432"),
        "user": os.getenv("POSTGRES_USER", "user").strip() or "user",
        "password": os.getenv("POSTGRES_PASSWORD", "password").strip() or "password",
        "dbname": os.getenv("POSTGRES_DB", "konsyltant").strip() or "konsyltant",
        "sqlite_path": os.path.join(PROJECT_ROOT, "konsyltant.db")
    }

    if db_url:
        if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
            try:
                clean_url = "postgresql://" + db_url.split("://", 1)[1]
                parsed = urllib.parse.urlparse(clean_url)
                if parsed.hostname:
                    config["host"] = parsed.hostname
                if parsed.port:
                    config["port"] = parsed.port
                if parsed.username:
                    config["user"] = urllib.parse.unquote(parsed.username)
                if parsed.password:
                    config["password"] = urllib.parse.unquote(parsed.password)
                if parsed.path:
                    config["dbname"] = parsed.path.lstrip("/")
            except Exception as e:
                logger.warning(f"Ошибка парсинга DATABASE_URL: {e}")
        elif db_url.startswith("sqlite:///"):
            config["sqlite_path"] = db_url.replace("sqlite:///", "", 1)
        elif db_url.startswith("sqlite://"):
            config["sqlite_path"] = db_url.replace("sqlite://", "", 1)

    return config


def list_backups(output_dir: Optional[str] = None) -> List[Dict]:
    """
    Возвращает список существующих бэкапов, отсортированных от новых к старым.
    """
    backup_dir = get_backup_dir(output_dir)
    items = []
    
    if not os.path.exists(backup_dir):
        return items

    for filename in os.listdir(backup_dir):
        if filename.startswith("."):
            continue
        if filename.endswith(".sql.gz") or filename.endswith(".dump") or filename.endswith(".sql"):
            filepath = os.path.join(backup_dir, filename)
            try:
                stat = os.stat(filepath)
                size_bytes = stat.st_size
                mtime = stat.st_mtime
                created_iso = datetime.fromtimestamp(mtime).isoformat()
                items.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size_bytes": size_bytes,
                    "size_human": format_bytes(size_bytes),
                    "created_at": created_iso,
                    "mtime": mtime
                })
            except Exception as e:
                logger.warning(f"Не удалось прочитать файл {filename}: {e}")

    items.sort(key=lambda x: x["mtime"], reverse=True)
    return items


def rotate_backups(
    backup_dir: Optional[str] = None, 
    retention_days: int = DEFAULT_RETENTION_DAYS, 
    max_backups: int = DEFAULT_MAX_BACKUPS,
    dry_run: bool = False
) -> List[str]:
    """
    Применяет политику удержания (Retention Policy):
    - Сохраняет не более max_backups файлов;
    - Удаляет дампы старше retention_days дней (при условии сохранения хотя бы 1 последнего дампа).
    Возвращает список имен удаленных файлов.
    """
    backups = list_backups(backup_dir)
    if not backups:
        return []

    cutoff_timestamp = time.time() - (retention_days * 86400)
    deleted_files = []

    for index, b_info in enumerate(backups):
        # Самый свежий дамп всегда сохраняется для гарантированного восстановления
        if index == 0:
            continue

        is_older_than_retention = b_info["mtime"] < cutoff_timestamp
        is_exceeding_max = index >= max_backups

        if is_older_than_retention or is_exceeding_max:
            file_path = b_info["filepath"]
            file_name = b_info["filename"]
            if dry_run:
                logger.info(f"[BACKUP ROTATION DRY-RUN] Будет удален устаревший дамп: {file_name}")
            else:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    logger.info(f"[BACKUP ROTATION] Удален устаревший дамп: {file_name} ({b_info['size_human']})")
                except Exception as e:
                    logger.error(f"[BACKUP ROTATION ERROR] Ошибка при удалении {file_name}: {e}")
            deleted_files.append(file_name)

    return deleted_files


def _dump_postgres_via_python(conn, filepath: str):
    """
    Фоллбэк создания текстового SQL-дампа PostgreSQL через psycopg2 (если pg_dump недоступен).
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [r[0] for r in cursor.fetchall()]

    with gzip.open(filepath, "wt", encoding="utf-8") as gz_out:
        gz_out.write("-- PostgreSQL Backup (Python Fallback Mode)\n")
        gz_out.write(f"-- Created At: {datetime.now().isoformat()}\n\n")
        gz_out.write("BEGIN;\n\n")

        for table in tables:
            gz_out.write(f"-- Table: {table}\n")
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;")
            cols = [r[0] for r in cursor.fetchall()]
            if not cols:
                continue

            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()
            col_list_str = ", ".join(f'"{c}"' for c in cols)

            for row in rows:
                val_strs = []
                for val in row:
                    if val is None:
                        val_strs.append("NULL")
                    elif isinstance(val, bool):
                        val_strs.append("TRUE" if val else "FALSE")
                    elif isinstance(val, (int, float)):
                        val_strs.append(str(val))
                    else:
                        escaped = str(val).replace("'", "''")
                        val_strs.append(f"'{escaped}'")
                row_vals_str = ", ".join(val_strs)
                gz_out.write(f"INSERT INTO {table} ({col_list_str}) VALUES ({row_vals_str});\n")
            gz_out.write("\n")

        gz_out.write("COMMIT;\n")


def create_backup(
    output_dir: Optional[str] = None,
    retention_days: int = DEFAULT_RETENTION_DAYS,
    max_backups: int = DEFAULT_MAX_BACKUPS,
    dry_run: bool = False
) -> Dict:
    """
    Создает сжатый дамп базы данных PostgreSQL (или SQLite в dev-режиме) с ротацией.
    """
    backup_dir = get_backup_dir(output_dir)
    db_config = get_db_config()
    
    conn = database.get_connection()
    is_sqlite = isinstance(conn, sqlite3.Connection)
    is_postgres = not is_sqlite and db_config["is_postgres"]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_konsyltant_{timestamp}.sql.gz"
    filepath = os.path.join(backup_dir, filename)

    logger.info(f"[BACKUP INITIATED] Запуск создания резервной копии. Тип БД: {'PostgreSQL' if is_postgres else 'SQLite'}")
    logger.info(f"[BACKUP TARGET] Файл: {filename} в {backup_dir}")

    if dry_run:
        conn.close()
        logger.info(f"[BACKUP DRY-RUN] Фактическая запись файла пропущена (dry-run=True).")
        rotated = rotate_backups(backup_dir, retention_days=retention_days, max_backups=max_backups, dry_run=True)
        return {
            "status": "ok",
            "dry_run": True,
            "filename": filename,
            "filepath": filepath,
            "size_bytes": 0,
            "size_human": "0 B",
            "created_at": datetime.now().isoformat(),
            "db_type": "postgres" if is_postgres else "sqlite",
            "rotated_backups": rotated
        }

    start_time = time.time()

    try:
        if is_postgres:
            pg_dump_path = shutil.which("pg_dump")
            if pg_dump_path:
                logger.info(f"[BACKUP METHOD] Использование нативного pg_dump ({pg_dump_path})...")
                env = os.environ.copy()
                if db_config["password"]:
                    env["PGPASSWORD"] = db_config["password"]
                
                cmd = [
                    pg_dump_path,
                    "-h", str(db_config["host"]),
                    "-p", str(db_config["port"]),
                    "-U", str(db_config["user"]),
                    "-d", str(db_config["dbname"]),
                    "--no-owner",
                    "--no-privileges",
                    "--clean",
                    "--if-exists"
                ]

                with gzip.open(filepath, "wb") as gz_file:
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                    shutil.copyfileobj(proc.stdout, gz_file)
                    proc.stdout.close()
                    stderr_data = proc.stderr.read()
                    proc.stderr.close()
                    code = proc.wait()

                    if code != 0:
                        err_text = stderr_data.decode("utf-8", errors="replace")
                        raise RuntimeError(f"pg_dump завершился с ошибкой (код {code}): {err_text}")
            else:
                logger.info("[BACKUP METHOD] Утилита pg_dump не обнаружена. Экспорт схемы и данных через psycopg2...")
                _dump_postgres_via_python(conn, filepath)
        else:
            # SQLite dev mode
            logger.info("[BACKUP METHOD] Экспорт SQLite базы данных через iterdump()...")
            with gzip.open(filepath, "wt", encoding="utf-8") as gz_file:
                for line in conn.iterdump():
                    gz_file.write(f"{line}\n")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    elapsed = time.time() - start_time
    size_bytes = os.path.getsize(filepath)
    size_human = format_bytes(size_bytes)
    logger.info(f"[BACKUP SUCCESS] Дамп успешно создан за {elapsed:.2f}с: {filename} ({size_human})")

    # Применение ротации
    rotated = rotate_backups(backup_dir, retention_days=retention_days, max_backups=max_backups, dry_run=False)

    return {
        "status": "ok",
        "dry_run": False,
        "filename": filename,
        "filepath": filepath,
        "size_bytes": size_bytes,
        "size_human": size_human,
        "created_at": datetime.now().isoformat(),
        "db_type": "postgres" if is_postgres else "sqlite",
        "elapsed_seconds": round(elapsed, 3),
        "rotated_backups": rotated
    }


def main():
    parser = argparse.ArgumentParser(
        description="Резервное копирование и ротация дампов базы данных ЦМЗ «Маленькая Страна»"
    )
    parser.add_argument("--output-dir", type=str, default=None, help="Директория сохранения дампов (по умолчанию: ./backups)")
    parser.add_argument("--retention-days", type=int, default=DEFAULT_RETENTION_DAYS, help="Количество дней хранения бэкапов (по умолчанию: 7)")
    parser.add_argument("--max-backups", type=int, default=DEFAULT_MAX_BACKUPS, help="Максимальное количество сохраняемых дампов (по умолчанию: 7)")
    parser.add_argument("--dry-run", action="store_true", help="Тестовый запуск без реальной записи и удаления файлов")
    parser.add_argument("--list", action="store_true", help="Показать список существующих бэкапов и выйти")

    args = parser.parse_args()

    if args.list:
        backups = list_backups(args.output_dir)
        print("=" * 70)
        print(f"📦 СПИСОК РЕЗЕРВНЫХ КОПИЙ ({len(backups)} шт.):")
        print("=" * 70)
        if not backups:
            print("  (Резервные копии отсутствуют)")
        else:
            for b in backups:
                print(f"  • {b['filename']} | Размер: {b['size_human']:<10} | Создан: {b['created_at']}")
        print("=" * 70)
        sys.exit(0)

    try:
        res = create_backup(
            output_dir=args.output_dir,
            retention_days=args.retention_days,
            max_backups=args.max_backups,
            dry_run=args.dry_run
        )
        print("\n" + "=" * 60)
        print("🎉 РЕЗЕРВНОЕ КОПИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("=" * 60)
        print(f"📁 Файл дампа:   {res['filename']}")
        print(f"💾 Размер:       {res['size_human']} ({res['size_bytes']} байт)")
        print(f"🗄️ Тип БД:       {res['db_type']}")
        print(f"⏱️ Время работы: {res.get('elapsed_seconds', 0)} с")
        if res.get('rotated_backups'):
            print(f"🧹 Ротация:      Удалено устаревших дампов: {len(res['rotated_backups'])} шт.")
        print("=" * 60 + "\n")
    except Exception as err:
        logger.error(f"❌ Критическая ошибка резервного копирования: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
