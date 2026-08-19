import os
import uuid
import json
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройка GigaChat (Сбер ИИ)
GIGACHAT_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_COMPLETIONS_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
MODEL = "GigaChat"
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")

SYSTEM_PROMPT_TEMPLATE = """
Ты — ИИ-Консультант, виртуальный медицинский помощник пациента.
Твоя задача — отвечать на вопросы пациента, опираясь ИСКЛЮЧИТЕЛЬНО на предоставленный ниже контекст из его РЕАЛЬНЫХ медицинских документов.

ЖЕСТКИЕ ПРАВИЛА (ZERO-HALLUCINATION & DYNAMIC MULTI-TENANT ISOLATION):
1. Ты ОБЯЗАН отвечать только на основе фактов из предоставленных документов данного конкретного пациента.
2. Если в документах нет информации, достаточной для ответа, ты ДОЛЖЕН ПРЯМО ОТВЕТИТЬ: "Извините, но в ваших документах нет информации об этом." Никаких выдуманных цифр и показателей!
3. Категорически запрещено выдумывать показатели или цитировать данные других людей.

КОНТЕКСТ ДОКУМЕНТОВ ДАННОГО ПАЦИЕНТА:
{context}
"""

def get_gigachat_token() -> str:
    auth_key = os.getenv("GIGACHAT_CREDENTIALS") or os.getenv("GIGACHAT_AUTH_KEY", "")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

    if not auth_key:
        print("[GIGACHAT ERROR] GIGACHAT_CREDENTIALS / GIGACHAT_AUTH_KEY не задан в .env")
        return None

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {auth_key}"
    }
    payload = {"scope": scope}

    try:
        res = requests.post(GIGACHAT_OAUTH_URL, headers=headers, data=payload, verify=False, timeout=15)
        if res.status_code == 200:
            return res.json().get("access_token")
        else:
            print(f"[GIGACHAT OAUTH ERROR] {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"[GIGACHAT OAUTH EXCEPTION] {e}")
        return None

def fetch_yandex_cache_json(folder_id: str) -> tuple[dict | None, bool]:
    """
    Ищет внутри папки пациента (folder_id) единственный файл, заканчивающийся на '_cache.json'.
    Возвращает (json_data, cache_found_flag).
    - Если кэш-файл не найден, возвращает (None, False).
    - Если кэш-файл найден и успешно выкачан, возвращает (cache_data, True).
    """
    if not YANDEX_DISK_TOKEN:
        print("[RAG ERROR] YANDEX_DISK_TOKEN не задан.")
        return None, False

    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}", "Accept": "application/json"}
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": folder_id, "limit": 100}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            items = res.json().get("_embedded", {}).get("items", [])
            cache_item = None
            for item in items:
                fname = item.get("name", "")
                if fname.endswith("_cache.json"):
                    cache_item = item
                    break

            if not cache_item:
                print(f"[RAG ETL STATUS] Файл кэша *_cache.json в папке '{folder_id}' не найден.")
                return None, False

            fpath = cache_item.get("path")
            file_url = cache_item.get("file")
            
            if not file_url:
                down_res = requests.get(url, headers=headers, params={"path": fpath}, timeout=10)
                if down_res.status_code == 200:
                    file_url = down_res.json().get("file")

            if file_url:
                content_res = requests.get(file_url, timeout=20)
                if content_res.status_code == 200:
                    cache_data = json.loads(content_res.content.decode('utf-8'))
                    print(f"[RAG CACHE SUCCESS] Загружен JSON-кэш для '{folder_id}' (Чанков в кэше: {len(cache_data.get('chunks', []))})")
                    return cache_data, True
    except Exception as e:
        print(f"[RAG CACHE FETCH EXCEPTION] Ошибка загрузки кэша для '{folder_id}': {e}")

    return None, False

def build_patient_context(folder_id: str) -> tuple[str, bool]:
    """
    Формирует контекст исключительно из готового JSON-кэша.
    Возвращает (context_text, cache_exists).
    """
    cache_data, cache_exists = fetch_yandex_cache_json(folder_id)
    if not cache_exists:
        return "", False

    chunks = cache_data.get("chunks", [])
    if not chunks:
        clean_name = folder_id.replace("disk:/", "").strip()
        return f"--- Карта Пациента: {clean_name} ---\nВ обработанном кэше пока нет содержательного текста.", True

    return "\n\n".join(chunks), True

def ask_consultant(user_message: str, folder_id: str) -> str:
    """
    Формирует контекст из массива "chunks" файла _cache.json конкретной папки folder_id и запрашивает ответ у GigaChat.
    Если файл кэша еще не создан, возвращает технический ответ.
    В случае сетевой ошибки, таймаута или исчерпания квоты (401/403) возвращает пользовательское сообщение о сбое.
    """
    context_text, cache_exists = build_patient_context(folder_id)
    
    if not cache_exists:
        return "Документы пациента еще обрабатываются. Пожалуйста, подождите пару минут и повторите вопрос."

    ERROR_MESSAGE = "⚠️ Ошибка: Сбой связи с ИИ или закончились токены. Пожалуйста, обратитесь к администратору."

    try:
        token = get_gigachat_token()
        if not token:
            return ERROR_MESSAGE

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_text)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.2
        }

        response = requests.post(GIGACHAT_COMPLETIONS_URL, headers=headers, json=payload, verify=False, timeout=30)
        
        if response.status_code in (401, 403):
            print(f"[GIGACHAT API ERROR] {response.status_code} Quota/Auth issue: {response.text}")
            return ERROR_MESSAGE

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"[GIGACHAT REQUEST ERROR] {e}")
        return ERROR_MESSAGE
    except Exception as e:
        print(f"[GIGACHAT EXCEPTION] {e}")
        return ERROR_MESSAGE

SUMMARY_SYSTEM_PROMPT_TEMPLATE = """
Ты — ведущий медицинский эксперт и клинический аналитик центра «Маленькая Страна».
Твоя задача — составить структурированное клиническое резюме медицинской карты пациента на основе предоставленного ниже контекста извлеченных медицинских документов.

ЖЕСТКИЕ ПРАВИЛА (ZERO-HALLUCINATION CLINICAL SUMMARY):
1. Опирайся ИСКЛЮЧИТЕЛЬНО на предоставленные документы данного пациента.
2. Не выдумывай медицинские факты, диагнозы, аллергии или препараты! Если информации по какому-либо пункту нет в документах, возвращай null или пустой массив [].
3. Твой ответ ДОЛЖЕН БЫТЬ СТРОГО В ФОРМАТЕ JSON без окружающего текста и блоков кода markdown со следующей структурой:
{{
  "anamnesis": "Краткая история болезни и текущее состояние",
  "diagnoses": ["Список диагнозов"],
  "contraindications": ["Критические противопоказания и аллергии"],
  "drug_interactions": ["Несовместимые препараты и риски лекарственных взаимодействий"],
  "recommendations": ["Краткие рекомендации по наблюдению"]
}}

КОНТЕКСТ МЕДИЦИНСКИХ ДОКУМЕНТОВ:
{context}
"""

def generate_medical_summary(folder_id: str) -> tuple[dict | None, str | None, bool]:
    """
    Генерирует структурированное клиническое резюме пациента через GigaChat API.
    Возвращает (summary_dict, raw_text, cache_exists).
    - Если кэш документов не найден: (None, None, False)
    - Если резюме успешно сгенерировано: (parsed_json_dict, raw_response, True)
    """
    context_text, cache_exists = build_patient_context(folder_id)
    if not cache_exists:
        return None, None, False

    token = get_gigachat_token()
    if not token:
        return {
            "anamnesis": "Не удалось подключиться к сервису ИИ (ошибка авторизации).",
            "diagnoses": [],
            "contraindications": [],
            "drug_interactions": [],
            "recommendations": []
        }, "GigaChat Auth Error", True

    system_prompt = SUMMARY_SYSTEM_PROMPT_TEMPLATE.format(context=context_text)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Сформируй клиническое резюме в формате JSON на основе контекста документов."}
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(GIGACHAT_COMPLETIONS_URL, headers=headers, json=payload, verify=False, timeout=40)
        if response.status_code in (401, 403):
            return {
                "anamnesis": "Сервис ИИ временно недоступен (лимит квоты токенов).",
                "diagnoses": [],
                "contraindications": [],
                "drug_interactions": [],
                "recommendations": []
            }, response.text, True

        response.raise_for_status()
        raw_content = response.json()["choices"][0]["message"]["content"]
        
        # Очистка от markdown блоков ```json ... ```
        cleaned = raw_content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            result = {
                "anamnesis": parsed.get("anamnesis", ""),
                "diagnoses": parsed.get("diagnoses", []) or [],
                "contraindications": parsed.get("contraindications", []) or [],
                "drug_interactions": parsed.get("drug_interactions", []) or [],
                "recommendations": parsed.get("recommendations", []) or []
            }
            return result, raw_content, True
        except Exception:
            return {
                "anamnesis": raw_content,
                "diagnoses": [],
                "contraindications": [],
                "drug_interactions": [],
                "recommendations": [],
                "raw_response": raw_content
            }, raw_content, True

    except Exception as e:
        print(f"[MEDICAL SUMMARY EXCEPTION] {e}")
        return {
            "anamnesis": f"Ошибка генерации резюме: {str(e)}",
            "diagnoses": [],
            "contraindications": [],
            "drug_interactions": [],
            "recommendations": [],
            "raw_response": str(e)
        }, str(e), True


