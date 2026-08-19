import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")

def get_yandex_files(folder_path):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    params = {"path": folder_path, "limit": 100}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            items = res.json().get("_embedded", {}).get("items", [])
            return items
    except Exception as e:
        print(f"Error reading {folder_path}: {e}")
    return []

def main():
    print("=== ИНСПЕКЦИЯ РЕАЛЬНЫХ ФАЙЛОВ В ПАПКАХ НА ЯНДЕКС.ДИСКЕ ===")
    
    folders = ["disk:/Александр Морозов", "disk:/Зоя Космодемьянская", "disk:/Павлик Морозов", "disk:/Новая папка"]
    for fpath in folders:
        print(f"\n--- Папка: {fpath} ---")
        items = get_yandex_files(fpath)
        if not items:
            print("  (Папка пуста или является файлом)")
        for item in items:
            print(f"  [{item.get('type')}] Name: '{item.get('name')}' | Size: {item.get('size')} | Download URL: {item.get('file')}")

if __name__ == "__main__":
    main()
