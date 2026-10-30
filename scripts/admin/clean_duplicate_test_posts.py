#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/admin/clean_duplicate_test_posts.py — Безопасная очистка базы данных от тестовых постов-клонов.

Выполняет:
  1. Создание резервной копии базы данных перед изменениями.
  2. Удаление из таблицы public_posts всех записей, созданных автотестами:
     - Заголовок содержит «Интерактивные упражнения для развития речи»
     - Либо обложка содержит ссылку «disk.yandex.ru/i/test_speech_cover.jpg».
  3. Удаление из таблицы public_library тестовых дубликатов:
     - Заголовок содержит «Сборник речевых сказок для малышей»
     - Либо обложка содержит ссылку «tales_cover.png».
  4. Вывод в консоль подробной статистики: сколько удалено и сколько осталось.
"""

import os
import sys
import shutil
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

# Обеспечиваем импорт модулей из корня проекта
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import database  # noqa: E402

def make_database_backup() -> str:
    """Создает резервную копию базы данных перед выполнением очистки."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    is_postgres = database.check_is_postgres()

    if is_postgres:
        backup_dir = PROJECT_ROOT / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        dump_path = backup_dir / f"konsyltant_pg_backup_{timestamp}.dump"
        db_url = os.getenv("DATABASE_URL")
        print(f"📦 [BACKUP] Создание дампа PostgreSQL: {dump_path}...")
        try:
            import subprocess
            cmd = ["pg_dump", "--format=custom", "--file", str(dump_path), db_url]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ [BACKUP] Резервная копия PostgreSQL создана: {dump_path}")
            return str(dump_path)
        except Exception as e:
            print(f"⚠️ [BACKUP WARNING] Не удалось выполнить pg_dump ({e}). Продолжаем с транзакционной защитой.")
            return ""
    else:
        # SQLite
        db_file = os.getenv("SQLITE_DB_PATH", os.getenv("DB_FILE", "konsyltant.db"))
        db_path = Path(db_file)
        if not db_path.is_absolute():
            db_path = PROJECT_ROOT / db_path

        if not db_path.exists():
            print(f"⚠️ [BACKUP] Файл БД не найден: {db_path}")
            return ""

        # Копируем в backups/ и локальный бэкап рядом с БД
        backup_dir = PROJECT_ROOT / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_dest = backup_dir / f"{db_path.name}.backup_{timestamp}"
        shutil.copy2(db_path, backup_dest)
        
        # Также локальная копия рядом для быстрого отката
        local_backup = db_path.parent / f"{db_path.name}.backup_{timestamp}"
        if local_backup != backup_dest:
            shutil.copy2(db_path, local_backup)

        print(f"✅ [BACKUP] Резервная копия SQLite создана:")
        print(f"   -> {backup_dest}")
        print(f"   -> {local_backup}")
        return str(backup_dest)

def clean_duplicate_test_posts(dry_run: bool = False):
    print("=" * 70)
    print("🧹 САНИРОВАНИЕ ТЕСТОВЫХ ДУБЛИКАТОВ СТАТЕЙ И МАТЕРИАЛОВ БИБЛИОТЕКИ")
    print("=" * 70)

    if dry_run:
        print("🔍 [РЕЖИМ ПРЕДПРОСМОТРА (DRY-RUN)]: Изменения в базу данных вноситься НЕ будут.\n")
    else:
        make_database_backup()
        print()

    conn = database.get_connection()
    cursor = conn.cursor()
    is_postgres = database.check_is_postgres()

    try:
        # --- 1. АНАЛИЗ И ОЧИСТКА public_posts ---
        database.execute_query(cursor, "SELECT count(*) FROM public_posts")
        total_posts_before = cursor.fetchone()[0]

        post_delete_condition = """
            title LIKE '%Интерактивные упражнения для развития речи%' 
            OR cover_image_url LIKE '%test_speech_cover.jpg%'
        """

        database.execute_query(cursor, f"SELECT count(*) FROM public_posts WHERE {post_delete_condition}")
        trash_posts_count = cursor.fetchone()[0]

        # --- 2. АНАЛИЗ И ОЧИСТКА public_library ---
        database.execute_query(cursor, "SELECT count(*) FROM public_library")
        total_library_before = cursor.fetchone()[0]

        library_delete_condition = """
            title LIKE '%Сборник речевых сказок для малышей%' 
            OR cover_image_url LIKE '%tales_cover.png%'
        """

        database.execute_query(cursor, f"SELECT count(*) FROM public_library WHERE {library_delete_condition}")
        trash_library_count = cursor.fetchone()[0]

        print(f"📊 СОСТОЯНИЕ ДО ОЧИСТКИ:")
        print(f"   • public_posts:   Всего: {total_posts_before} | Клонов к удалению: {trash_posts_count}")
        print(f"   • public_library: Всего: {total_library_before} | Клонов к удалению: {trash_library_count}")
        print("-" * 70)

        if not dry_run:
            # Выполняем фактическое удаление
            database.execute_query(cursor, f"DELETE FROM public_posts WHERE {post_delete_condition}")
            deleted_posts = cursor.rowcount if hasattr(cursor, 'rowcount') else trash_posts_count

            database.execute_query(cursor, f"DELETE FROM public_library WHERE {library_delete_condition}")
            deleted_library = cursor.rowcount if hasattr(cursor, 'rowcount') else trash_library_count

            conn.commit()

            # Дефрагментация файла SQLite (VACUUM)
            if not is_postgres:
                try:
                    conn.close()
                    db_file = os.getenv("SQLITE_DB_PATH", os.getenv("DB_FILE", "konsyltant.db"))
                    db_path = Path(db_file)
                    if not db_path.is_absolute():
                        db_path = PROJECT_ROOT / db_path
                    vacuum_conn = sqlite3.connect(str(db_path))
                    vacuum_conn.execute("VACUUM")
                    vacuum_conn.close()
                    conn = database.get_connection()
                    cursor = conn.cursor()
                except Exception as e:
                    print(f"ℹ️ [VACUUM NOTE] Оптимизация размера файла пропущена: {e}")

            # Проверяем итоговое количество
            database.execute_query(cursor, "SELECT count(*) FROM public_posts")
            total_posts_after = cursor.fetchone()[0]

            database.execute_query(cursor, "SELECT count(*) FROM public_library")
            total_library_after = cursor.fetchone()[0]

            print(f"✅ РЕЗУЛЬТАТ ОЧИСТКИ:")
            print(f"   • public_posts:   Удалено: {deleted_posts} мусорных записей | Осталось материалов: {total_posts_after}")
            print(f"   • public_library: Удалено: {deleted_library} мусорных записей | Осталось материалов: {total_library_after}")
            print("=" * 70)
            print("🎉 База данных успешно очищена от тестовых клонов!")
        else:
            print(f"ℹ️ [DRY-RUN] Будет удалено: {trash_posts_count} постов и {trash_library_count} материалов библиотеки.")
            print(f"ℹ️ [DRY-RUN] Останется: {total_posts_before - trash_posts_count} постов и {total_library_before - trash_library_count} материалов.")
            print("=" * 70)

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [ОШИБКА ПРИ ОЧИСТКЕ]: {e}", file=sys.stderr)
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Очистка базы данных от тестовых постов-клонов")
    parser.add_argument("--dry-run", action="store_true", help="Только показать статистику без фактического удаления")
    args = parser.parse_args()

    clean_duplicate_test_posts(dry_run=args.dry_run)
