import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

from database import init_db
from folder_watcher import scan_folders

def main():
    print("=== Сброс БД для папок 'Зоя Космодемьянская' и 'Александр Морозов' ===")
    init_db()

    conn = sqlite3.connect("konsyltant.db")
    cursor = conn.cursor()
    
    # Сброс записей
    cursor.execute("""
        DELETE FROM patient_access 
        WHERE gdrive_folder_id LIKE '%Зоя%' 
           OR gdrive_folder_id LIKE '%Космодемьянская%'
           OR gdrive_folder_id LIKE '%Александр%'
           OR gdrive_folder_id LIKE '%Александр Морозов%'
    """)
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"[DB RESET SUCCESS] Удалено старых записей из базы данных: {deleted_count}")
    print("\n--- Запуск scan_folders() для повторного обнаружения и отправки email 250 OK ---")
    scan_folders()

if __name__ == "__main__":
    main()
