import os
import sys
import json
import secrets
import string
import argparse
import bcrypt
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()

from database import init_db, get_connection, execute_query
from folder_watcher import (
    upload_json_to_yandex_disk,
    publish_yandex_disk_resource,
    build_and_upload_folder_cache
)

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "https://xn--g1aj3a.site")
if not BASE_URL or ":8000" in BASE_URL:
    BASE_URL = "https://xn--g1aj3a.site"
BASE_URL = BASE_URL.rstrip("/")

def check_yandex_folder_exists(folder_id: str) -> tuple:
    """
    Проверяет существование папки на Яндекс.Диске через REST API.
    Возвращает (exists: bool, items: list, error_msg: str)
    """
    if not YANDEX_DISK_TOKEN:
        return False, [], "YANDEX_DISK_TOKEN не задан в переменных окружения"
    
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {
        "Authorization": f"OAuth {YANDEX_DISK_TOKEN}",
        "Accept": "application/json"
    }
    params = {"path": folder_id, "limit": 100}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            data = res.json()
            items = data.get("_embedded", {}).get("items", [])
            return True, items, ""
        elif res.status_code == 404:
            return False, [], f"Папка '{folder_id}' не найдена на Яндекс.Диске (HTTP 404)"
        else:
            return False, [], f"Ошибка Яндекс.Диск API: HTTP {res.status_code} ({res.text})"
    except Exception as e:
        return False, [], f"Сетевое исключение при обращении к Яндекс.Диску: {e}"

def generate_secure_passcode(length=10) -> str:
    """Генерирует легкочитаемый, но криптографически стойкий пароль."""
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    # Гарантируем наличие заглавной буквы, строчной буквы, цифры и спецсимвола
    pwd = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%&*")
    ]
    for _ in range(length - 4):
        pwd.append(secrets.choice(alphabet))
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)

def seed_production_patient(folder_name: str, custom_password: str = None) -> dict:
    """
    Основная функция сидирования боевого пациента:
    1. Валидация папки на Яндекс.Диске.
    2. Проверка или формирование RAG-кэша.
    3. Создание / обновление записи доступа в patient_access.
    4. Генерация и вывод доступов родителя.
    """
    clean_folder_name = folder_name.strip()
    if clean_folder_name.startswith("disk:/"):
        patient_folder_id = clean_folder_name
        clean_folder_name = clean_folder_name.replace("disk:/", "")
    else:
        patient_folder_id = f"disk:/{clean_folder_name}"

    print("=" * 65)
    print(f"🚀 СИДИРОВАНИЕ БОЕВОГО ПАЦИЕНТА: '{clean_folder_name}'")
    print(f"📂 Путь на Яндекс.Диске: {patient_folder_id}")
    print("=" * 65)

    # 1. Проверка существования папки на Яндекс.Диске
    folder_exists, items, error_msg = check_yandex_folder_exists(patient_folder_id)
    if not folder_exists:
        print(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {error_msg}")
        print("ℹ️ Продолжаем создание записи доступа в БД (папка может быть загружена позже).")
    else:
        print(f"✅ Папка найдена на Яндекс.Диске! Обнаружено файлов: {len(items)}")

    # 2. Проверка наличия RAG-кэша
    cache_filename = f"_{clean_folder_name}_cache.json"
    cache_exists = any(item.get("name") == cache_filename for item in items)
    
    if cache_exists:
        print(f"✅ RAG-кэш '{cache_filename}' уже присутствует на Яндекс.Диске.")
    else:
        print(f"ℹ️ RAG-кэш '{cache_filename}' отсутствует. Он будет автоматически создан воркером folder_watcher.")

    # 3. Инициализация и подключение к БД
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем, есть ли уже запись в patient_access
    execute_query(cursor, "SELECT id, access_token, password_hash FROM patient_access WHERE gdrive_folder_id = ?", (patient_folder_id,))
    existing = cursor.fetchone()

    passcode = custom_password if custom_password else (generate_secure_passcode() if not existing else None)
    
    if existing:
        record_id, access_token, existing_pw_hash = existing
        if passcode:
            password_hash = bcrypt.hashpw(passcode.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            execute_query(cursor, """
                UPDATE patient_access
                SET password_hash = ?, role = 'PATIENT', is_verified = TRUE
                WHERE id = ?
            """, (password_hash, record_id))
            print(f"✅ Существующая запись (ID {record_id}) обновлена. Пароль сброшен на новый.")
        else:
            execute_query(cursor, """
                UPDATE patient_access
                SET role = 'PATIENT', is_verified = TRUE
                WHERE id = ?
            """, (record_id,))
            print(f"✅ Существующая запись (ID {record_id}) актуализирована. Старый пароль сохранен.")
            passcode = "[Прежний пароль пациента сохранен]"
    else:
        access_token = secrets.token_urlsafe(32)
        if not passcode:
            passcode = generate_secure_passcode()
        password_hash = bcrypt.hashpw(passcode.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, is_verified)
            VALUES (?, ?, ?, 'PATIENT', TRUE)
        """, (access_token, password_hash, patient_folder_id))
        print(f"✅ Новая запись боевого пациента успешно создана в patient_access.")

    conn.commit()
    conn.close()

    patient_login_url = f"{BASE_URL}/app/?token={access_token}"

    print("-" * 65)
    print("📋 ДОСТУПЫ ДЛЯ РОДИТЕЛЯ ПАЦИЕНТА:")
    print(f"🔗 Ссылка для входа:  {patient_login_url}")
    print(f"🔑 Пароль:            {passcode}")
    print(f"📁 Папка документов:  {patient_folder_id}")
    print(f"🛡️ Роль в системе:    PATIENT")
    print("-" * 65)

    return {
        "status": "success",
        "folder_name": clean_folder_name,
        "patient_folder_id": patient_folder_id,
        "access_token": access_token,
        "passcode": passcode,
        "login_url": patient_login_url
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Сидирование боевого пациента из папки на Яндекс.Диске")
    parser.add_argument("folder", nargs="?", default="Дюзгёрен Арон Альп", help="Имя папки пациента на Яндекс.Диске")
    parser.add_argument("--password", "-p", default=None, help="Опциональный пароль для пациента")
    args = parser.parse_args()

    seed_production_patient(args.folder, args.password)
