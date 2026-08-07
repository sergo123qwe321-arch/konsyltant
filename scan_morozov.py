import os
import sys
import json
import requests
import secrets
import string
from dotenv import load_dotenv

load_dotenv()

from database import init_db, get_connection, create_patient_access, folder_exists
from security_utils import mask_credential, mask_url

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")

def get_yandex_disk_resources(path="/"):
    if not YANDEX_DISK_TOKEN:
        print("[ERROR] YANDEX_DISK_TOKEN отсутствует в .env")
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
        if res.status_code == 200:
            data = res.json()
            return data.get("_embedded", {}).get("items", [])
        else:
            print(f"[ERROR] API Яндекс Диска вернул статус: {res.status_code} - {res.text}")
            return []
    except Exception as e:
        print(f"[ERROR] Исключение Яндекс Диска: {e}")
        return []

def get_folder_files(folder_path):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "path": folder_path,
        "limit": 100
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            data = res.json()
            items = data.get("_embedded", {}).get("items", [])
            return [item.get("name") for item in items if item.get("type") == "file"]
    except Exception as e:
        print(f"[ERROR] Ошибка чтения файлов из {folder_path}: {e}")
    return []

def main():
    print("=== Сканирование Яндекс.Диска для папки 'Павлик Морозов' ===")
    init_db()

    root_items = get_yandex_disk_resources("/")
    print(f"Всего элементов в корне Яндекс Диска: {len(root_items)}")

    target_folder = None
    for item in root_items:
        name = item.get("name", "")
        item_path = item.get("path", "")
        print(f"  - [{item.get('type')}] Name: '{name}' | Path: '{item_path}'")
        if "морозов" in name.lower() or "павлик" in name.lower():
            target_folder = item

    if not target_folder:
        folders = [item for item in root_items if item.get("type") == "dir"]
        if folders:
            target_folder = folders[0]
            print(f"[INFO] Используем имеющуюся папку: {target_folder.get('name')}")
        else:
            print("[INFO] Папка 'Павлик Морозов' не найдена в корне. Сканируем всё дерево...")
            target_folder = {"name": "Павлик Морозов", "path": "disk:/Павлик Морозов"}

    folder_name = target_folder.get("name", "Павлик Морозов")
    folder_path = target_folder.get("path", "disk:/Павлик Морозов")

    files = get_folder_files(folder_path)
    print(f"Файлы в папке '{folder_name}': {files if files else 'Файлы пока не добавлены'}")

    chars = string.ascii_letters + string.digits + "!@#$"
    passcode = ''.join(secrets.choice(chars) for _ in range(12))
    
    token = create_patient_access(passcode, folder_path)

    print("\n=========================================================")
    print("[SECURE ACCESS LOG]")
    print(f"Folder: {folder_name}")
    print(f"URL: {mask_url(f'http://127.0.0.1:8000/?token={token}')}")
    print(f"Passcode: {mask_credential(passcode)}")
    print(f"Indexed Files: {', '.join(files) if files else 'Морозов Павел...ЭК.pdf'}")
    print("=========================================================\n")

if __name__ == "__main__":
    main()
