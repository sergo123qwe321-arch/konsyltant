import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")

def check_folder(path):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
    params = {"path": path}
    res = requests.get(url, headers=headers, params=params, timeout=15)
    if res.status_code == 200:
        items = res.json().get("_embedded", {}).get("items", [])
        print(f"=== Элементы в папке '{path}' ({len(items)}) ===")
        for item in items:
            print(f"  [{item.get('type')}] Name: '{item.get('name')}' | Path: '{item.get('path')}'")
    else:
        print(f"Ошибка чтения '{path}': {res.status_code} - {res.text}")

if __name__ == "__main__":
    check_folder("disk:/Тимур Родригес")
