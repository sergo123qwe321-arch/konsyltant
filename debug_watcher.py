import os
import sys
import traceback

sys.stdout.reconfigure(encoding='utf-8')

from database import init_db
from folder_watcher import scan_folders, get_yandex_disk_folders

def debug_run():
    print("=========================================================")
    print(" 1. ПРОВЕРКА ВИДИМОСТИ ВСЕХ РЕСУРСОВ НА ЯНДЕКС ДИСКЕ")
    print("=========================================================")
    items = get_yandex_disk_folders("/")
    print(f"Всего элементов в корне Яндекс Диска: {len(items)}")
    for idx, item in enumerate(items, 1):
        print(f"  {idx}. [{item.get('type').upper()}] Name: '{item.get('name')}' | Path: '{item.get('path')}'")

    print("\n=========================================================")
    print(" 2. ИЗОЛИРОВАННЫЙ ПРОГОН FOLDER_WATCHER")
    print("=========================================================")
    try:
        init_db()
        scan_folders()
        print("\n[DEBUG WATCHER SUCCESS] Прогон выполнен успешно!")
    except Exception as e:
        print("\n=========================================================")
        print(" CRITICAL WORKER CRASH TRACEBACK:")
        print("=========================================================")
        traceback.print_exc()
        print("=========================================================\n")

if __name__ == "__main__":
    debug_run()
