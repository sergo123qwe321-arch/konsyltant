import os
import sys
import secrets
import string
import requests
import logging
from dotenv import load_dotenv

from database import folder_exists, create_patient_access
from notification_service import NotificationService
from security_utils import mask_credential, mask_url

load_dotenv()

logger = logging.getLogger(__name__)

TARGET_EMAIL = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "konsultantms@yandex.com")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def get_yandex_disk_folders(path="/"):
    """Сканирует ресурсы Яндекс.Диска по указанному пути"""
    if not YANDEX_DISK_TOKEN:
        logging.error("[FOLDER WATCHER ERROR] YANDEX_DISK_TOKEN не задан в .env.")
        return []

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    params = {"path": path, "limit": 100}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            data = res.json()
            items = data.get("_embedded", {}).get("items", [])
            return [item for item in items if item.get("type") in ("dir", "file")]
        else:
            logging.error(f"[FOLDER WATCHER ERROR] Яндекс Диск API вернул статус: {res.status_code}")
            return []
    except Exception as e:
        logging.error(f"[FOLDER WATCHER ERROR] Исключение Яндекс Диск API: {e}")
        return []

def scan_folders():
    """
    Фоновое сканирование новых папок на Яндекс.Диске с высокой отказоустойчивостью и защитой от CWE-532.
    """
    print(f"\n[FOLDER WATCHER] Сканирование ресурсов Яндекс.Диска. Целевой email: {TARGET_EMAIL}")
    
    items = get_yandex_disk_folders("/")
    if not items:
        print("[FOLDER WATCHER] Папки на Яндекс Диске не обнаружены или сбой соединения.")
        return

    new_count = 0
    for item in items:
        try:
            item_path = item.get("path")
            item_name = item.get("name")
            
            # Проверяем наличие в базе данных
            if not folder_exists(item_path):
                print(f"\n[FOLDER WATCHER DETECTED] [NEW ITEM] Найдена новая папка/файл: '{item_name}' (Path: {item_path})")
                
                # Генерация доступа
                password = generate_random_password()
                access_token = create_patient_access(password, item_path)
                
                # Безопасное маскированное логирование
                masked_token = mask_credential(access_token)
                masked_pass = mask_credential(password)
                print(f"[SECURE FOLDER WATCHER LOG] Зарегистрирован новый доступ для '{item_name}' | Token: {masked_token} | Passcode: {masked_pass}")
                
                # Отправка уведомления на Yandex SMTP
                print(f"[FOLDER WATCHER] Отправка Email-уведомления для '{item_name}' на {TARGET_EMAIL}...")
                sent_ok = NotificationService.send_welcome_email(
                    recipient_email=TARGET_EMAIL,
                    access_token=access_token,
                    passcode=password,
                    folder_name=item_name,
                    base_url=BASE_URL
                )
                
                if sent_ok:
                    print(f"[FOLDER WATCHER SUCCESS] [OK] Письмо для '{item_name}' успешно отправлено через Yandex SMTP!")
                else:
                    print(f"[FOLDER WATCHER LOG] Отправка SMTP не завершена.")
                    
                new_count += 1
        except Exception as e:
            logging.error(f"[FOLDER WATCHER ERROR] Ошибка обработки объекта '{item.get('name')}': {e}")
            print(f"[FOLDER WATCHER ERROR] Ошибка обработки папки '{item.get('name')}': {e}")
            continue

    if new_count == 0:
        print("[FOLDER WATCHER] Новых необработанных папок нет.")
    else:
        print(f"[FOLDER WATCHER] Обработано новых элементов: {new_count}")

if __name__ == "__main__":
    scan_folders()
