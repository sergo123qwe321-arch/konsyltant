import os
import sys
import secrets
import string
import requests
import logging
from dotenv import load_dotenv

import json
from datetime import datetime, timezone
from document_parser import parse_document_bytes, chunk_text

from database import folder_exists, create_patient_access
from notification_service import NotificationService
from security_utils import mask_credential, mask_url

load_dotenv()

logger = logging.getLogger(__name__)

TARGET_EMAIL = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "konsultantms@yandex.com")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "https://xn--g1aj3a.site")

# Конфигурация исключений папок
EXCLUDED_FOLDERS = [f.strip() for f in os.getenv('EXCLUDED_FOLDERS', 'Загрузки,Trash,Archive,Корзина').split(',') if f.strip()]

# Хранилище последних логов ETL для диагностического эндпоинта администратора
LAST_ETL_LOGS: dict[str, list[str]] = {}

def record_etl_log(folder_name: str, message: str):
    clean_key = folder_name.replace("disk:/", "").strip("/").strip()
    if clean_key not in LAST_ETL_LOGS:
        LAST_ETL_LOGS[clean_key] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    LAST_ETL_LOGS[clean_key].append(entry)
    if len(LAST_ETL_LOGS[clean_key]) > 50:
        LAST_ETL_LOGS[clean_key].pop(0)

def get_last_etl_logs(folder_name: str, limit: int = 10) -> list[str]:
    clean_key = folder_name.replace("disk:/", "").strip("/").strip()
    logs = LAST_ETL_LOGS.get(clean_key, [])
    return logs[-limit:]

def should_process_folder(folder_name: str) -> bool:
    clean_name = folder_name.replace("disk:/", "").strip("/").strip()
    for excluded in EXCLUDED_FOLDERS:
        clean_excluded = excluded.strip().lower()
        if clean_name.lower() == clean_excluded or clean_name.lower().startswith(clean_excluded + "/"):
            logger.info(f"⏭️ Пропуск исключенной папки: {folder_name}")
            return False
    return True

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def download_yandex_file_bytes(fpath: str, direct_download_url: str = None) -> bytes:
    """Скачивает содержимое файла с Яндекс.Диска."""
    if direct_download_url:
        try:
            res = requests.get(direct_download_url, timeout=15)
            if res.status_code == 200:
                return res.content
        except Exception as e:
            logger.warning(f"Прямое скачивание не удалось, запрашиваем по API: {e}")

    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}", "Accept": "application/json"}
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    try:
        res = requests.get(url, headers=headers, params={"path": fpath}, timeout=15)
        if res.status_code == 200:
            down_url = res.json().get("file")
            if down_url:
                file_res = requests.get(down_url, timeout=15)
                if file_res.status_code == 200:
                    return file_res.content
    except Exception as e:
        logger.error(f"[YANDEX DOWNLOAD ERROR] Ошибка скачивания '{fpath}': {e}")
    return b""

def upload_json_to_yandex_disk(disk_path: str, payload: dict) -> bool:
    """
    Загружает JSON-данные на Яндекс.Диск:
    1. GET https://cloud-api.yandex.net/v1/disk/resources/upload?path=<path>&overwrite=true
    2. PUT <href> с телом JSON
    """
    if not YANDEX_DISK_TOKEN:
        logger.error("[YANDEX DISK UPLOAD ERROR] YANDEX_DISK_TOKEN не задан.")
        return False

    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    upload_api_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {"path": disk_path, "overwrite": "true"}

    try:
        res = requests.get(upload_api_url, headers=headers, params=params, timeout=15)
        if res.status_code != 200:
            logger.error(f"[YANDEX DISK UPLOAD ERROR] Не удалось получить href ({res.status_code}): {res.text}")
            return False

        upload_href = res.json().get("href")
        if not upload_href:
            logger.error("[YANDEX DISK UPLOAD ERROR] Поле href отсутствует в ответе API.")
            return False

        json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
        put_headers = {"Content-Type": "application/json; charset=utf-8"}
        
        put_res = requests.put(upload_href, data=json_bytes, headers=put_headers, timeout=15)
        if put_res.status_code in (200, 201):
            logger.info(f"[YANDEX DISK UPLOAD] Файл кэша '{disk_path}' загружен (Размер: {len(json_bytes)} байт)")
            return True
        else:
            logger.error(f"[YANDEX DISK UPLOAD ERROR] PUT вернул статус {put_res.status_code}: {put_res.text}")
            return False
    except Exception as e:
        logger.error(f"[YANDEX DISK UPLOAD EXCEPTION] Исключение при загрузке '{disk_path}': {e}")
        return False

def build_and_upload_folder_cache(folder_path: str, folder_name: str) -> str:
    """
    Выполняет ETL-процесс для папки пациента:
    - Парсит документы (игнорируя файлы на '_')
    - Разбивает текст на чанки
    - Формирует и загружает _{clean_folder_name}_cache.json на Яндекс.Диск
    - Публикует кэш-файл и возвращает его public_url
    """
    clean_folder_name = folder_name.replace(" ", "_")
    cache_filename = f"_{clean_folder_name}_cache.json"
    norm_folder_path = folder_path.rstrip("/")
    cache_disk_path = f"{norm_folder_path}/{cache_filename}"

    record_etl_log(folder_name, f"ETL запуск для '{folder_name}' ({folder_path})")
    logger.info(f"🔍 Найдена новая папка: {folder_name}")

    # Получаем содержимое папки
    items = get_yandex_disk_folders(folder_path)
    file_items = [it for it in items if it.get("type") == "file" and not it.get("name", "").startswith("_")]
    file_count = len(file_items)
    
    record_etl_log(folder_name, f"Скачивание файлов: {file_count} файлов обнаружено")
    logger.info(f"📥 Скачивание файлов: {file_count} файлов")

    all_chunks = []
    pages_processed = 0
    pages_total = 0

    for item in file_items:
        try:
            fname = item.get("name", "")
            fpath = item.get("path")
            mime_type = item.get("mime_type", "")
            pages_total += 1
            
            logger.info(f"📄 Обработка файла: '{fname}'")
            file_bytes = download_yandex_file_bytes(fpath, item.get("file"))
            if file_bytes:
                text = parse_document_bytes(file_bytes, fname, mime_type)
                if text and text.strip() and not text.startswith("[Неподдерживаемый") and not text.startswith("[Ошибка"):
                    pages_processed += 1
                    chunks = chunk_text(text, chunk_size=1000, overlap=100)
                    for chunk in chunks:
                        all_chunks.append(f"--- Файл: {fname} ---\n{chunk}")
                    record_etl_log(folder_name, f"Успешно обработан '{fname}' -> {len(chunks)} чанков")
                else:
                    record_etl_log(folder_name, f"Файл '{fname}' не содержит извлекаемого текста или ошибка парсера")
            else:
                record_etl_log(folder_name, f"Не удалось скачать байты для '{fname}'")
        except Exception as file_err:
            err_msg = f"Сбой обработки файла '{item.get('name', 'N/A')}': {file_err}"
            logger.error(f"[ETL PARSE ERROR] {err_msg}")
            record_etl_log(folder_name, err_msg)

    chunk_count = len(all_chunks)
    logger.info(f"🔤 OCR-обработка: {pages_processed}/{pages_total} страниц")
    logger.info(f"📝 Создано чанков: {chunk_count}")
    record_etl_log(folder_name, f"OCR-обработка: {pages_processed}/{pages_total} страниц, создано чанков: {chunk_count}")

    payload = {
        "patient_folder": folder_name,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "chunks": all_chunks
    }

    logger.info(f"💾 Сохранение кэша: {cache_filename}")
    record_etl_log(folder_name, f"Сохранение кэша на Яндекс.Диск: {cache_disk_path}")
    uploaded = upload_json_to_yandex_disk(cache_disk_path, payload)
    if not uploaded:
        record_etl_log(folder_name, "Ошибка загрузки JSON-кэша на Яндекс.Диск")
        return ""

    cache_public_url = publish_yandex_disk_resource(cache_disk_path)
    record_etl_log(folder_name, f"Кэш опубликован: {mask_url(cache_public_url) if cache_public_url else 'N/A'}")
    return cache_public_url

def publish_yandex_disk_resource(path: str) -> str:
    """
    Публикует ресурс на Яндекс.Диске и возвращает публичную ссылку (public_url).
    1. POST/PUT запрос к https://cloud-api.yandex.net/v1/disk/resources/publish?path=<path>
    2. GET запрос к /v1/disk/resources?path=<path> для извлечения public_url
    """
    if not YANDEX_DISK_TOKEN:
        logger.error("[YANDEX DISK PUBLISH ERROR] YANDEX_DISK_TOKEN не задан.")
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
                logger.info(f"[YANDEX DISK PUBLISH] Успешно опубликован ресурс '{path}' | Public URL: {mask_url(public_url)}")
                return public_url
            else:
                logger.warning(f"[YANDEX DISK PUBLISH] public_url не найден для ресурса '{path}'")
        else:
            logger.error(f"[YANDEX DISK PUBLISH ERROR] Ошибка получения инфо для '{path}': {info_res.status_code}")
    except Exception as e:
        logger.error(f"[YANDEX DISK PUBLISH EXCEPTION] Исключение при публикации '{path}': {e}")

    return ""

def get_yandex_disk_folders(path="/"):
    """Сканирует ресурсы Яндекс.Диска по указанному пути, игнорируя системные файлы/папки с '_'"""
    if not YANDEX_DISK_TOKEN:
        logger.error("[FOLDER WATCHER ERROR] YANDEX_DISK_TOKEN не задан в .env.")
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
                if name.startswith("_"):
                    continue
                if item.get("type") in ("dir", "file"):
                    valid_items.append(item)
            return valid_items
        else:
            logger.error(f"[FOLDER WATCHER ERROR] Яндекс Диск API вернул статус: {res.status_code}")
            return []
    except Exception as e:
        logger.error(f"[FOLDER WATCHER ERROR] Исключение Яндекс Диск API: {e}")
        return []

def scan_folders():
    """
    Фоновое сканирование новых папок на Яндекс.Диске с высокой отказоустойчивостью и защитой от CWE-532.
    """
    logger.info(f"📋 Исключенные из сканирования папки: {EXCLUDED_FOLDERS}")
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

            # Пропуск исключенных папок
            if not should_process_folder(item_name):
                continue
            
            # Проверяем наличие в базе данных
            if not folder_exists(item_path):
                logger.info(f"🔍 Найдена новая папка: {item_name}")
                record_etl_log(item_name, f"Обнаружена новая папка: {item_name} ({item_path})")
                
                # 1. Выполнение ETL-процесса: сканирование, OCR/парсер, чанкинг, запись в _{folder_name}_cache.json на Яндекс.Диск
                cache_public_url = build_and_upload_folder_cache(item_path, item_name)

                # 2. Публикация самой папки на Яндекс.Диске для получения public_url
                public_url = publish_yandex_disk_resource(item_path)
                
                # 3. Генерация доступа
                password = generate_random_password()
                access_token = create_patient_access(password, item_path)
                logger.info(f"🔐 Генерация токена: {access_token[:8]}...")
                record_etl_log(item_name, f"Сгенерирован доступ токен={access_token[:8]}...")
                
                # Безопасное маскированное логирование
                masked_token = mask_credential(access_token)
                masked_pass = mask_credential(password)
                masked_pub_url = mask_url(public_url) if public_url else "N/A"
                masked_cache_url = mask_url(cache_public_url) if cache_public_url else "N/A"
                print(f"[SECURE FOLDER WATCHER LOG] Зарегистрирован новый доступ для '{item_name}' | Token: {masked_token} | Passcode: {masked_pass} | Folder URL: {masked_pub_url} | Cache URL: {masked_cache_url}")
                
                # 4. Отправка уведомления на Yandex SMTP
                logger.info(f"📧 Отправка email: {TARGET_EMAIL}")
                record_etl_log(item_name, f"Отправка уведомления на {TARGET_EMAIL}")
                sent_ok = NotificationService.send_welcome_email(
                    recipient_email=TARGET_EMAIL,
                    access_token=access_token,
                    passcode=password,
                    folder_name=item_name,
                    base_url=BASE_URL,
                    folder_public_url=public_url,
                    cache_public_url=cache_public_url
                )
                
                if sent_ok:
                    record_etl_log(item_name, f"Email успешно отправлен на {TARGET_EMAIL}")
                    print(f"[FOLDER WATCHER SUCCESS] [OK] Письмо для '{item_name}' успешно отправлено через Yandex SMTP!")
                else:
                    record_etl_log(item_name, f"Сбой отправки email на {TARGET_EMAIL}")
                    print(f"[FOLDER WATCHER LOG] Отправка SMTP не завершена.")
                    
                new_count += 1
            else:
                # Если папка уже зарегистрирована, проверяем наличие файла кэша (если его еще не было)
                clean_fname = item_name.replace(" ", "_")
                cache_check_path = f"{item_path.rstrip('/')}/_{clean_fname}_cache.json"
                try:
                    info_url = "https://cloud-api.yandex.net/v1/disk/resources"
                    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}", "Accept": "application/json"}
                    check_res = requests.get(info_url, headers=headers, params={"path": cache_check_path}, timeout=15)
                    if check_res.status_code == 404:
                        logger.info(f"🔍 Найдена существующая папка без кэша: {item_name}. Запуск фонового ETL...")
                        record_etl_log(item_name, "Папка зарегистрирована, но кэш отсутствует. Запуск ETL...")
                        build_and_upload_folder_cache(item_path, item_name)
                except Exception as ex:
                    pass
        except Exception as e:
            err_log = f"[ETL ERROR] Сбой обработки папки '{item.get('name', 'N/A')}': {e}"
            logger.error(err_log)
            print(err_log)
            continue

    if new_count == 0:
        print("[FOLDER WATCHER] Новых необработанных папок нет.")
    else:
        print(f"[FOLDER WATCHER] Обработано новых элементов: {new_count}")

if __name__ == "__main__":
    scan_folders()
