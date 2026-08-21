import os
import sys
import json
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
from folder_watcher import upload_json_to_yandex_disk, publish_yandex_disk_resource

PATIENT_FOLDER_NAME = "Тестовый Пациент"
PATIENT_FOLDER_ID = f"disk:/{PATIENT_FOLDER_NAME}"
ACCESS_TOKEN = "patient_producer_test_2026"
PLAIN_PASSWORD = "TestPatient2026!"
BASE_URL = os.getenv("BASE_URL", "https://xn--g1aj3a.site")
if not BASE_URL or ":8000" in BASE_URL:
    BASE_URL = "https://xn--g1aj3a.site"
BASE_URL = BASE_URL.rstrip("/")

def seed_test_patient():
    print("=" * 60)
    print("🚀 СИДИРОВАНИЕ ТЕСТОВОГО ПАЦИЕНТА ДЛЯ ПРОДЮСЕРА")
    print("=" * 60)

    # 1. Инициализация БД
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Хэшируем пароль
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(PLAIN_PASSWORD.encode('utf-8'), salt).decode('utf-8')

    # 2. Проверяем существование записи
    execute_query(cursor, "SELECT id, access_token, gdrive_folder_id FROM patient_access WHERE gdrive_folder_id = ? OR access_token = ?", (PATIENT_FOLDER_ID, ACCESS_TOKEN))
    existing = cursor.fetchone()

    if existing:
        record_id = existing[0]
        execute_query(cursor, """
            UPDATE patient_access 
            SET access_token = ?, password_hash = ?, gdrive_folder_id = ?, role = 'PATIENT', is_verified = TRUE
            WHERE id = ?
        """, (ACCESS_TOKEN, password_hash, PATIENT_FOLDER_ID, record_id))
        print(f"✅ Существующая запись пациента (ID {record_id}) успешно обновлена в patient_access.")
    else:
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, is_verified)
            VALUES (?, ?, ?, 'PATIENT', TRUE)
        """, (ACCESS_TOKEN, password_hash, PATIENT_FOLDER_ID))
        print("✅ Новая запись тестового пациента успешно создана в patient_access.")

    conn.commit()
    conn.close()

    # 3. Подготовка и загрузка JSON-кэша на Яндекс.Диск
    yandex_token = os.getenv("YANDEX_DISK_TOKEN", "")
    cache_status = "Пропущено (нет токена)"
    
    if yandex_token:
        # Создаем папку на Яндекс.Диске, если её еще нет
        headers = {"Authorization": f"OAuth {yandex_token}", "Accept": "application/json"}
        mkdir_url = "https://cloud-api.yandex.net/v1/disk/resources"
        try:
            requests.put(mkdir_url, headers=headers, params={"path": PATIENT_FOLDER_ID}, timeout=10)
        except Exception:
            pass

        sample_chunks = [
            (
                "--- Файл: Первичная_нейропсихологическая_диагностика.pdf ---\n"
                "Пациент: Тестовый Пациент (Возраст: 5 лет 4 месяца).\n"
                "Анамнез и статус: Задержка речевого развития (ЗРР 2-3 уровня), лёгкие моторные дисфункции, "
                "синдром дефицита внимания с гиперактивностью (СДВГ лёгкой степени). "
                "Интеллект и понимание обращенной речи сохранны в полном объёме."
            ),
            (
                "--- Файл: Заключение_логопеда_дефектолога.pdf ---\n"
                "Логопедический статус: Фонетико-фонематическое недоразвитие речи (ФФНР), дизартрический компонент. "
                "Словарный запас ниже возрастной нормы, трудности построения сложных грамматических конструкций."
            ),
            (
                "--- Файл: План_коррекции_и_рекомендации.pdf ---\n"
                "Рекомендации и назначения:\n"
                "1. Индивидуальные занятия с логопедом-дефектологом 3 раза в неделю (артикуляционная гимнастика, постановка звуков).\n"
                "2. Курс нейродинамической гимнастики и сенсорной интеграции (2 раза в неделю).\n"
                "3. Консультация детского невролога (курсовой приём поливитаминов группы B, глицин).\n"
                "4. Режим дня: ограничение экранного времени (до 30 минут в день), регулярный дневной сон.\n"
                "Противопоказания: ноотропные стимулирующие препараты в вечернее время."
            )
        ]

        payload = {
            "patient_folder": PATIENT_FOLDER_NAME,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "chunks": sample_chunks
        }

        clean_file_name = PATIENT_FOLDER_NAME.replace(" ", "_")
        cache_path = f"{PATIENT_FOLDER_ID}/_{clean_file_name}_cache.json"
        uploaded = upload_json_to_yandex_disk(cache_path, payload)
        if uploaded:
            publish_yandex_disk_resource(cache_path)
            publish_yandex_disk_resource(PATIENT_FOLDER_ID)
            cache_status = f"✅ Загружен на Яндекс.Диск ({len(sample_chunks)} чанка) по пути '{cache_path}'"
        else:
            cache_status = "⚠️ Сбой загрузки на Яндекс.Диск"

    login_url = f"{BASE_URL}/app/?token={ACCESS_TOKEN}"

    print("-" * 60)
    print("📋 CREDENTIALS ТЕСТОВОГО ПАЦИЕНТА:")
    print(f"🔗 Ссылка для входа: {login_url}")
    print(f"🔑 Пароль:           {PLAIN_PASSWORD}")
    print(f"📁 Папка пациента:   {PATIENT_FOLDER_ID}")
    print(f"💾 Статус RAG-кэша:  {cache_status}")
    print("=" * 60)

if __name__ == "__main__":
    seed_test_patient()

