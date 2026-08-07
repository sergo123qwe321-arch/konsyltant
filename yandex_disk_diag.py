import os
import sys
import json
import traceback
import requests
from dotenv import load_dotenv

load_dotenv()

from database import init_db, get_connection, create_patient_access, folder_exists
from notification_service import NotificationService
from security_utils import mask_credential, mask_url

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")

def get_yandex_disk_folders(path="/"):
    """Получает список папок на Яндекс Диске через REST API"""
    if not YANDEX_DISK_TOKEN:
        print("[YANDEX DISK DIAG ERROR] YANDEX_DISK_TOKEN не найден в .env")
        return []

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "path": path,
        "limit": 100
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"[YANDEX DISK DIAG] GET Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            items = data.get("_embedded", {}).get("items", [])
            folders = [item for item in items if item.get("type") == "dir"]
            return folders
        else:
            print(f"[YANDEX DISK DIAG ERROR] Ошибка API Яндекс Диска: {res.status_code} - {res.text}")
            return []
    except Exception as e:
        print(f"[YANDEX DISK DIAG ERROR] Исключение при запросе к Яндекс Диску: {e}")
        return []

def run_diagnostics():
    print("=========================================================")
    print(" 1. ДИАГНОСТИКА YANDEX DISK СКАНИРОВАНИЯ")
    print("=========================================================")
    init_db()
    
    folders = get_yandex_disk_folders("/")
    print(f"Обнаружено папок на Яндекс Диске: {len(folders)}")
    for f in folders:
        print(f"  - Папка: '{f.get('name')}' | Path: '{f.get('path')}' | Created: {f.get('created')}")

    print("\n=========================================================")
    print(" 2. ДИАГНОСТИКА YANDEX SMTP (С СНИМКОМ TRACEBACK)")
    print("=========================================================")
    try:
        test_folder = folders[0].get("name") if folders else "Тестовый_Пациент"
        print(f"Вызов NotificationService.send_welcome_email для папки: {test_folder}")
        sent_status = NotificationService.send_welcome_email(
            recipient_email="konsultantms@yandex.com",
            access_token="real_diag_access_token_123",
            passcode="RealPasscode123!",
            folder_name=test_folder
        )
        print(f"Результат отправки почты: {sent_status}")
    except Exception as e:
        print("\n[SMTP TRACEBACK CAPTURED]:")
        traceback.print_exc()

    print("\n=========================================================")
    print(" 3. РЕГИСТРАЦИЯ ПАПОК И ЗАПРОС К БАЗЕ ДАННЫХ")
    print("=========================================================")
    for f in folders:
        f_id = f.get("path")
        f_name = f.get("name")
        if not folder_exists(f_id):
            print(f"[+] Сохранение новой папки с Яндекс Диска в БД: {f_name}")
            import secrets, string
            chars = string.ascii_letters + string.digits + "!@#$"
            pw = ''.join(secrets.choice(chars) for _ in range(12))
            token = create_patient_access(pw, f_id)
            print(f"    Сгенерирован токен: {mask_credential(token)} | Пароль: {mask_credential(pw)}")

    # Запрос актуальных данных из базы
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, access_token, gdrive_folder_id, created_at FROM patient_access ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    print(f"\nЗаписей в таблице patient_access: {len(rows)}")
    for r in rows:
        print(f"  [DB ROW] ID: {r[0]} | Token: {mask_credential(r[1])} | Folder/Path: {r[2]} | Date: {r[3]}")

    if rows:
        last_row = rows[0]
        token = last_row[1]
        folder_name = last_row[2]
        print("\n=========================================================")
        print("[SECURE DIAGNOSTIC LOG]")
        print(f"Folder Name: {folder_name}")
        print(f"URL: {mask_url(f'http://127.0.0.1:8000/?token={token}')}")
        print("=========================================================\n")

if __name__ == "__main__":
    run_diagnostics()
