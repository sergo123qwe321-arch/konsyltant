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

def publish_yandex_disk_resource(path: str) -> str:
    """
    Публикует ресурс на Яндекс.Диске и возвращает публичную ссылку (public_url).
    1. POST/PUT запрос к https://cloud-api.yandex.net/v1/disk/resources/publish?path=<path>
    2. GET запрос к /v1/disk/resources?path=<path> для извлечения public_url
    """
    if not YANDEX_DISK_TOKEN:
        logging.error("[YANDEX DISK PUBLISH ERROR] YANDEX_DISK_TOKEN не задан.")
        return ""

    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    publish_url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
    
    try:
        # 1. Запрос на публикацию ресурса
        res = requests.put(publish_url, headers=headers, params={"path": path}, timeout=15)
        if res.status_code not in (200, 409):
            res = requests.post(publish_url, headers=headers, params={"path": path}, timeout=15)

        # 2. GET запрос к метаданным ресурса для извлечения public_url
        info_url = "https://cloud-api.yandex.net/v1/disk/resources"
        info_res = requests.get(info_url, headers=headers, params={"path": path}, timeout=15)
        if info_res.status_code == 200:
            public_url = info_res.json().get("public_url", "")
            if public_url:
                print(f"[YANDEX DISK PUBLISH] Успешно опубликован ресурс '{path}' | Public URL: {mask_url(public_url)}")
                return public_url
            else:
                logging.warning(f"[YANDEX DISK PUBLISH] public_url не найден для ресурса '{path}'")
        else:
            logging.error(f"[YANDEX DISK PUBLISH ERROR] Ошибка получения инфо для '{path}': {info_res.status_code}")
    except Exception as e:
        logging.error(f"[YANDEX DISK PUBLISH EXCEPTION] Исключение при публикации '{path}': {e}")

    return ""

def get_yandex_disk_folders(path="/"):
    """Сканирует ресурсы Яндекс.Диска по указанному пути, игнорируя системные файлы/папки с '_'"""
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
            valid_items = []
            for item in items:
                name = item.get("name", "")
                # Строгое фильтрование системных элементов, начинающихся с '_'
                if name.startswith("_"):
                    continue
                if item.get("type") in ("dir", "file"):
                    valid_items.append(item)
            return valid_items
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
            item_name = item.get("name", "")
            
            # Дополнительная проверка на фильтрацию объектов с префиксом '_'
            if item_name.startswith("_"):
                print(f"[FOLDER WATCHER IGNORE] Пропуск системного объекта: '{item_name}'")
                continue
            
            # Проверяем наличие в базе данных
            if not folder_exists(item_path):
                print(f"\n[FOLDER WATCHER DETECTED] [NEW ITEM] Найдена новая папка/файл: '{item_name}' (Path: {item_path})")
                
                # Публикация ресурса на Яндекс.Диске для получения public_url
                public_url = publish_yandex_disk_resource(item_path)
                
                # Генерация доступа
                password = generate_random_password()
                access_token = create_patient_access(password, item_path)
                
                # Безопасное маскированное логирование
                masked_token = mask_credential(access_token)
                masked_pass = mask_credential(password)
                masked_pub_url = mask_url(public_url) if public_url else "N/A"
                print(f"[SECURE FOLDER WATCHER LOG] Зарегистрирован новый доступ для '{item_name}' | Token: {masked_token} | Passcode: {masked_pass} | Public URL: {masked_pub_url}")
                
                # Отправка уведомления на Yandex SMTP
                print(f"[FOLDER WATCHER] Отправка Email-уведомления для '{item_name}' на {TARGET_EMAIL}...")
                sent_ok = NotificationService.send_welcome_email(
                    recipient_email=TARGET_EMAIL,
                    access_token=access_token,
                    passcode=password,
                    folder_name=item_name,
                    base_url=BASE_URL,
                    folder_public_url=public_url
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
