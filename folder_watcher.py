import os
import sys

# Настройка безопасной кодировки консоли для Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import secrets
import string
import requests
import logging
from dotenv import load_dotenv

import json
import time
from datetime import datetime, timezone
from document_parser import parse_document_bytes, chunk_text

from database import folder_exists, create_patient_access, save_etl_metric
from notification_service import NotificationService
from security_utils import mask_credential, mask_url

load_dotenv()

logger = logging.getLogger(__name__)

TARGET_EMAIL = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "konsultantms@yandex.com")
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "https://xn--g1aj3a.site")

# Конфигурация исключений папок
EXCLUDED_FOLDERS = [f.strip() for f in os.getenv('EXCLUDED_FOLDERS', 'Загрузки,Trash,Archive,Корзина').split(',') if f.strip()]

# Максимальное количество файлов для обработки за один цикл синхронизации (защита от перегрузки CPU/OCR)
MAX_SYNC_BATCH = int(os.getenv("ETL_MAX_SYNC_BATCH", "25"))

# Конфигурация суточного интервала фонового сканирования (Scheduler)
FOLDER_SCAN_INTERVAL_HOURS = float(os.getenv("FOLDER_SCAN_INTERVAL_HOURS", "24"))
FOLDER_SCAN_INTERVAL_SECONDS = int(os.getenv("FOLDER_SCAN_INTERVAL_SECONDS", str(int(FOLDER_SCAN_INTERVAL_HOURS * 3600))))

# Хранилище последних логов ETL для диагностического эндпоинта администратора
LAST_ETL_LOGS: dict[str, list[str]] = {}

# Heartbeat отслеживания жизнеспособности ETL-воркера
LAST_ETL_HEARTBEAT: float = time.time()

def update_etl_heartbeat():
    global LAST_ETL_HEARTBEAT
    LAST_ETL_HEARTBEAT = time.time()

def get_last_etl_heartbeat() -> float:
    return LAST_ETL_HEARTBEAT

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

def safe_yandex_request(method, url, max_retries=3, **kwargs):
    """
    Выполняет HTTP-запрос к Яндекс.Диску с автоматическими повторами при сетевых сбоях и SSL EOF.
    """
    timeout = kwargs.pop("timeout", 25)
    for attempt in range(max_retries):
        try:
            return method(url, timeout=timeout, **kwargs)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt == max_retries - 1:
                logger.error(f"[YANDEX RETRY EXHAUSTED] Ошибка запроса к {url} после {max_retries} попыток: {e}")
                raise
            time.sleep(1.0 * (attempt + 1))

def download_yandex_file_bytes(fpath: str, direct_download_url: str = None) -> bytes:
    """Скачивает содержимое файла с Яндекс.Диска."""
    if direct_download_url:
        try:
            res = safe_yandex_request(requests.get, direct_download_url, timeout=25)
            if res.status_code == 200:
                return res.content
        except Exception as e:
            logger.warning(f"Прямое скачивание не удалось, запрашиваем по API: {e}")

    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}", "Accept": "application/json"}
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    try:
        res = safe_yandex_request(requests.get, url, headers=headers, params={"path": fpath}, timeout=25)
        if res.status_code == 200:
            down_url = res.json().get("file")
            if down_url:
                file_res = safe_yandex_request(requests.get, down_url, timeout=25)
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
        res = safe_yandex_request(requests.get, upload_api_url, headers=headers, params=params, timeout=25)
        if res.status_code != 200:
            logger.error(f"[YANDEX DISK UPLOAD ERROR] Не удалось получить href ({res.status_code}): {res.text}")
            return False

        upload_href = res.json().get("href")
        if not upload_href:
            logger.error("[YANDEX DISK UPLOAD ERROR] Поле href отсутствует в ответе API.")
            return False

        json_bytes = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
        put_headers = {"Content-Type": "application/json; charset=utf-8"}
        
        put_res = safe_yandex_request(requests.put, upload_href, data=json_bytes, headers=put_headers, timeout=25)
        if put_res.status_code in (200, 201):
            logger.info(f"[YANDEX DISK UPLOAD] Файл кэша '{disk_path}' загружен (Размер: {len(json_bytes)} байт)")
            return True
        else:
            logger.error(f"[YANDEX DISK UPLOAD ERROR] PUT вернул статус {put_res.status_code}: {put_res.text}")
            return False
    except Exception as e:
        logger.error(f"[YANDEX DISK UPLOAD EXCEPTION] Исключение при загрузке '{disk_path}': {e}")
        return False

def get_all_yandex_disk_files(folder_path: str) -> tuple[list[dict], int]:
    """
    Рекурсивно обходит директорию folder_path на Яндекс.Диске без ограничения глубины,
    собирая полный список файлов (type == 'file') с сохранением относительных путей.
    Возвращает (список файлов с метаданными, количество обойденных поддиректорий).
    """
    if not YANDEX_DISK_TOKEN:
        logger.error("[FOLDER WATCHER ERROR] YANDEX_DISK_TOKEN не задан в .env.")
        return [], 0

    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    url = "https://cloud-api.yandex.net/v1/disk/resources"

    norm_root = folder_path.rstrip("/") + "/"
    all_files = []
    subfolder_count = 0
    dirs_to_visit = [folder_path]
    visited_dirs = set()

    while dirs_to_visit:
        current_dir = dirs_to_visit.pop(0)
        norm_current = current_dir.rstrip("/")
        if norm_current in visited_dirs:
            continue
        visited_dirs.add(norm_current)

        if norm_current != folder_path.rstrip("/"):
            subfolder_count += 1

        offset = 0
        limit = 100
        while True:
            params = {"path": current_dir, "limit": limit, "offset": offset}
            try:
                res = safe_yandex_request(requests.get, url, headers=headers, params=params, timeout=25)
                if res.status_code != 200:
                    logger.error(f"[FOLDER WATCHER ERROR] Ошибка получения ресурсов '{current_dir}': {res.status_code}")
                    break
                data = res.json()
                embedded = data.get("_embedded", {})
                items = embedded.get("items", [])
                if not items:
                    break

                for item in items:
                    name = item.get("name", "")
                    if name.startswith("_"):
                        continue
                    item_type = item.get("type")
                    item_path = item.get("path", "")

                    if item_type == "file":
                        # Относительный путь от корня папки пациента
                        if item_path.startswith(norm_root):
                            rel_path = item_path[len(norm_root):]
                        else:
                            rel_path = name
                        rel_path = rel_path.replace("\\", "/").lstrip("/")
                        item_dict = dict(item)
                        item_dict["relative_path"] = rel_path
                        all_files.append(item_dict)

                    elif item_type == "dir":
                        dir_name = item.get("name", "")
                        if should_process_folder(dir_name):
                            dirs_to_visit.append(item_path)

                total = embedded.get("total", 0)
                offset += len(items)
                if offset >= total or len(items) < limit:
                    break
            except Exception as e:
                logger.error(f"[FOLDER WATCHER ERROR] Исключение при обходе '{current_dir}': {e}")
                break

    return all_files, subfolder_count

def build_and_upload_folder_cache(folder_path: str, folder_name: str, max_files_to_process: int = None) -> str:
    """
    Выполняет инкрементальный ETL-процесс для папки пациента с рекурсивным обходом:
    - Рекурсивно сканирует все подпапки Яндекс.Диска.
    - Сравнивает с существующим _cache.json (новая схема с files).
    - Удаляет чанки удаленных файлов.
    - Обрабатывает только новые или измененные файлы (по mtime/etag/size).
    - Пропускает неизмененные файлы без повторного OCR.
    - Собирает плоскую проекцию chunks для обратной совместимости с rag.py.
    - Загружает обновленный кэш и возвращает public_url.
    """
    start_ts = time.time()
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    clean_folder_name = folder_name.replace(" ", "_")
    cache_filename = f"_{clean_folder_name}_cache.json"
    norm_folder_path = folder_path.rstrip("/")
    cache_disk_path = f"{norm_folder_path}/{cache_filename}"

    record_etl_log(folder_name, f"ETL запуск для '{folder_name}' ({folder_path}) в {started_at}")
    logger.info(f"🔍 Рекурсивный ETL/синхронизация для папки: {folder_name}")

    # 1. Рекурсивное получение всех файлов во всех поддиректориях
    all_files, subfolder_count = get_all_yandex_disk_files(folder_path)
    file_count = len(all_files)

    # 2. Загрузка существующего кэша (если есть)
    existing_cache = None
    cache_bytes = download_yandex_file_bytes(cache_disk_path)
    if cache_bytes:
        try:
            existing_cache = json.loads(cache_bytes.decode('utf-8'))
        except Exception as e:
            logger.warning(f"Не удалось прочитать существующий кэш '{cache_disk_path}': {e}")
            existing_cache = None

    files_cache = {}
    if existing_cache and isinstance(existing_cache, dict):
        if "files" in existing_cache and isinstance(existing_cache["files"], dict):
            files_cache = dict(existing_cache["files"])
        elif "chunks" in existing_cache:
            logger.info(f"Обнаружен устаревший формат кэша для '{folder_name}'. Выполняется миграция...")
            record_etl_log(folder_name, "Обнаружен кэш старого формата, выполняется структурирование")
            files_cache = {}

    # 3. Дифференциальный анализ: удаленные, новые, измененные, неизмененные
    disk_files_map = {f["relative_path"]: f for f in all_files}
    deleted_files = [rel for rel in files_cache if rel not in disk_files_map]

    unchanged_files = []
    to_process = []

    for rel_path, f_item in disk_files_map.items():
        disk_mod = str(f_item.get("modified") or f_item.get("md5") or f_item.get("sha256") or "")
        disk_size = f_item.get("size")

        if rel_path in files_cache:
            c_entry = files_cache[rel_path]
            c_mod = str(c_entry.get("modified") or "")
            c_size = c_entry.get("size")
            if c_mod == disk_mod and c_size == disk_size and "chunks" in c_entry:
                unchanged_files.append(rel_path)
                continue

        to_process.append(f_item)

    record_etl_log(
        folder_name,
        f"Дифференциальный анализ: обойдено {subfolder_count} подпапок. Всего на Диске: {file_count}, "
        f"без изменений: {len(unchanged_files)}, к обработке: {len(to_process)}, удалено: {len(deleted_files)}"
    )
    logger.info(
        f"⚡ [ETL DIFF] '{folder_name}': {subfolder_count} подпапок, {len(unchanged_files)} без изм., "
        f"{len(to_process)} к обработке, {len(deleted_files)} удалено"
    )

    # Если изменений нет и кэш валиден
    if not to_process and not deleted_files and existing_cache and "files" in existing_cache:
        record_etl_log(folder_name, "Все файлы актуальны, изменений нет. Обновление кэша пропущено.")
        logger.info(f"⏭️ Папка '{folder_name}' полностью актуальна, пропуск повторного OCR.")
        return publish_yandex_disk_resource(cache_disk_path)

    # 4. Удаление удаленных файлов из кэша
    for rel_path in deleted_files:
        del files_cache[rel_path]
        record_etl_log(folder_name, f"Удален файл из кэша: '{rel_path}'")

    # 5. Применение ограничения батча (если задано)
    if max_files_to_process and max_files_to_process > 0 and len(to_process) > max_files_to_process:
        logger.info(f"Ограничение пакета обработки для '{folder_name}': {max_files_to_process} из {len(to_process)} файлов")
        record_etl_log(folder_name, f"Пакетная обработка: {max_files_to_process} из {len(to_process)} файлов в текущем цикле")
        batch_to_process = to_process[:max_files_to_process]
    else:
        batch_to_process = to_process

    # 6. Обработка новых и измененных файлов
    pages_processed = 0
    pages_total = len(batch_to_process)
    errors_count = 0

    for item in batch_to_process:
        rel_path = item.get("relative_path", item.get("name", ""))
        fname = item.get("name", "")
        fpath = item.get("path")
        mime_type = item.get("mime_type", "")
        disk_mod = str(item.get("modified") or item.get("md5") or item.get("sha256") or "")
        disk_size = item.get("size")

        logger.info(f"📄 Обработка файла: '{rel_path}'")
        try:
            file_bytes = download_yandex_file_bytes(fpath, item.get("file"))
            if not file_bytes:
                errors_count += 1
                record_etl_log(folder_name, f"Не удалось скачать байты для '{rel_path}'")
                continue

            text = parse_document_bytes(file_bytes, fname, mime_type)
            if text and text.strip() and not text.startswith("[Неподдерживаемый") and not text.startswith("[Ошибка") and not text.startswith("[Отказ") and not text.startswith("[Не удалось"):
                pages_processed += 1
                raw_chunks = chunk_text(text, chunk_size=1000, overlap=100)
                file_chunks = [f"--- Файл: {rel_path} ---\n{chunk}" for chunk in raw_chunks]
                files_cache[rel_path] = {
                    "modified": disk_mod,
                    "size": disk_size if disk_size is not None else len(file_bytes),
                    "chunks": file_chunks
                }
                record_etl_log(folder_name, f"Успешно обработан '{rel_path}' -> {len(file_chunks)} чанков")
            else:
                errors_count += 1
                files_cache[rel_path] = {
                    "modified": disk_mod,
                    "size": disk_size if disk_size is not None else len(file_bytes),
                    "chunks": []
                }
                record_etl_log(folder_name, f"Файл '{rel_path}' не содержит извлекаемого текста или ошибка формата")
        except Exception as file_err:
            errors_count += 1
            err_msg = f"Сбой обработки файла '{rel_path}': {file_err}"
            logger.error(f"[ETL PARSE ERROR] {err_msg}")
            record_etl_log(folder_name, err_msg)

    # 7. Сборка плоской проекции чанков
    all_chunks = []
    for rel_path in sorted(files_cache.keys()):
        all_chunks.extend(files_cache[rel_path].get("chunks", []))

    chunk_count = len(all_chunks)
    logger.info(f"🔤 OCR/Парсер завершен: {pages_processed}/{pages_total} файлов обработано, итоговых чанков: {chunk_count}")
    record_etl_log(folder_name, f"OCR/Парсер: {pages_processed}/{pages_total} файлов обработано, создано чанков в кэше: {chunk_count}")

    # 8. Формирование новой схемы кэша
    payload = {
        "patient_folder": folder_name,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "files": files_cache,
        "chunks": all_chunks
    }

    logger.info(f"💾 Сохранение кэша: {cache_filename}")
    record_etl_log(folder_name, f"Сохранение кэша на Яндекс.Диск: {cache_disk_path}")
    uploaded = upload_json_to_yandex_disk(cache_disk_path, payload)

    # 9. Расчет метрик и сохранение в БД
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    duration_seconds = round(time.time() - start_ts, 2)
    avg_time_per_file = round(duration_seconds / len(batch_to_process), 2) if batch_to_process else 0.0

    try:
        save_etl_metric(
            folder_name=folder_name,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=duration_seconds,
            file_count=file_count,
            pages_processed=pages_processed,
            chunks_created=chunk_count,
            errors_count=errors_count,
            avg_time_per_file_seconds=avg_time_per_file
        )
        logger.info(f"⚡ [ETL METRICS] Папка '{folder_name}': {file_count} файлов ({subfolder_count} подпапок), {duration_seconds}с (среднее: {avg_time_per_file}с/файл)")
    except Exception as metric_err:
        logger.error(f"[ETL METRICS ERROR] Ошибка сохранения метрик в БД: {metric_err}")

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
        res = safe_yandex_request(requests.put, publish_url, headers=headers, params={"path": path}, timeout=25)
        if res.status_code not in (200, 409):
            res = safe_yandex_request(requests.post, publish_url, headers=headers, params={"path": path}, timeout=25)

        # 2. GET запрос к метаданным ресурса для извлечения public_url
        info_url = "https://cloud-api.yandex.net/v1/disk/resources"
        info_res = safe_yandex_request(requests.get, info_url, headers=headers, params={"path": path}, timeout=25)
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
        res = safe_yandex_request(requests.get, url, headers=headers, params=params, timeout=25)
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
    update_etl_heartbeat()
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
                # Если папка уже зарегистрирована, выполняем дифференциальную синхронизацию кэша
                try:
                    logger.info(f"🔄 Проверка дифференциальной синхронизации для '{item_name}'...")
                    build_and_upload_folder_cache(item_path, item_name, max_files_to_process=MAX_SYNC_BATCH)
                except Exception as ex:
                    logger.error(f"[ETL SYNC ERROR] Ошибка синхронизации папки '{item_name}': {ex}")
        except Exception as e:
            err_log = f"[ETL ERROR] Сбой обработки папки '{item.get('name', 'N/A')}': {e}"
            logger.error(err_log)
            print(err_log)
            continue

    if new_count == 0:
        print("[FOLDER WATCHER] Новых необработанных папок нет.")
    else:
        print(f"[FOLDER WATCHER] Обработано новых элементов: {new_count}")

def sync_patient_folder(patient_name: str, max_files: int = None) -> bool:
    """
    Точечная синхронизация папки конкретного пациента на Яндекс.Диске через CLI.
    """
    clean_name = patient_name.strip().replace("disk:/", "").strip("/")
    folder_path = f"disk:/{clean_name}"

    print(f"\n============================================================")
    print(f"[CLI TARGET SYNC] Пациент: '{clean_name}'")
    print(f"[CLI TARGET SYNC] Путь на Яндекс.Диске: {folder_path}")
    print(f"============================================================")
    logger.info(f"[CLI TARGET SYNC] Запуск синхронизации для '{clean_name}' ({folder_path})")

    try:
        batch_limit = max_files if max_files is not None else 35
        if max_files == 0:
            batch_limit = None
        cache_url = build_and_upload_folder_cache(folder_path, clean_name, max_files_to_process=batch_limit)
        if cache_url:
            print(f"[OK] Синхронизация папки '{clean_name}' успешно завершена.")
            print(f"[OK] Ссылка на кэш: {cache_url}")
            return True
        else:
            print(f"[INFO] Синхронизация завершена: кэш не обновлен или изменений не обнаружено.")
            return False
    except Exception as e:
        print(f"[ERROR] Ошибка точечной синхронизации для '{clean_name}': {e}")
        logger.error(f"[CLI TARGET SYNC ERROR] {e}")
        return False

def watcher_loop():
    """
    Фоновый бесконечный цикл периодического сканирования с настраиваемым суточным интервалом.
    """
    logger.info(f"⏰ [FOLDER WATCHER SCHEDULER] Запущен фоновый воркер (интервал: {FOLDER_SCAN_INTERVAL_HOURS} ч / {FOLDER_SCAN_INTERVAL_SECONDS} с)")
    while True:
        try:
            scan_folders()
        except Exception as e:
            logger.error(f"[FOLDER WATCHER SCHEDULER ERROR] Ошибка в цикле сканирования: {e}")
        time.sleep(FOLDER_SCAN_INTERVAL_SECONDS)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ETL-сервис мониторинга и синхронизации папок Яндекс.Диска")
    parser.add_argument("--patient", type=str, default=None, help="Имя или путь папки конкретного пациента для точечной синхронизации")
    parser.add_argument("--limit", type=int, default=None, help="Максимальное количество файлов для обработки (по умолчанию все или ETL_MAX_SYNC_BATCH)")
    parser.add_argument("--daemon", action="store_true", help="Запуск в режиме постоянного фонового демона")
    args = parser.parse_args()

    if args.patient:
        sync_patient_folder(args.patient, max_files=args.limit)
    elif args.daemon:
        watcher_loop()
    else:
        scan_folders()
