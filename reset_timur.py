import sqlite3
import os
import sys
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

from database import init_db
from folder_watcher import scan_folders

def main():
    print("=== Сброс статуса для папки 'Тимур Родригес' ===")
    init_db()

    conn = sqlite3.connect("konsyltant.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM patient_access 
        WHERE gdrive_folder_id LIKE '%Тимур%' 
           OR gdrive_folder_id LIKE '%Родригес%'
    """)
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"[DB RESET SUCCESS] Удалено старых записей для Тимура: {deleted_count}")
    print("\n--- Запуск отказоустойчивого scan_folders() ---")
    scan_folders()

if __name__ == "__main__":
    main()
