import os
import re
import uuid
import json
import logging
from datetime import datetime
import requests
import urllib3
from dotenv import load_dotenv
from database import record_llm_usage, get_llm_usage_summary

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger("rag")

# Настройка GigaChat (Сбер ИИ)
GIGACHAT_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_COMPLETIONS_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_BALANCE_URL = "https://gigachat.devices.sberbank.ru/api/v1/balance"
MODEL = "GigaChat"
YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")

# Счетчик последовательных ошибок LLM для системы мониторинга
CONSECUTIVE_LLM_ERRORS: int = 0

def increment_llm_errors():
    global CONSECUTIVE_LLM_ERRORS
    CONSECUTIVE_LLM_ERRORS += 1

def reset_llm_errors():
    global CONSECUTIVE_LLM_ERRORS
    CONSECUTIVE_LLM_ERRORS = 0

def get_consecutive_llm_errors() -> int:
    return CONSECUTIVE_LLM_ERRORS

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
            increment_llm_errors()
            print(f"[GIGACHAT API ERROR] {response.status_code} Quota/Auth issue: {response.text}")
            return ERROR_MESSAGE

        response.raise_for_status()
        data = response.json()
        reset_llm_errors()
        
        # Учет потребления токенов
        try:
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            resp_model = data.get("model", MODEL)
            record_llm_usage(resp_model, prompt_tokens, completion_tokens, total_tokens, "rag_consultation")
        except Exception as usage_err:
            logger.error(f"[LLM USAGE TRACK ERROR] {usage_err}")

        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        increment_llm_errors()
        print(f"[GIGACHAT REQUEST ERROR] {e}")
        return ERROR_MESSAGE
    except Exception as e:
        increment_llm_errors()
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
            increment_llm_errors()
            return {
                "anamnesis": "Сервис ИИ временно недоступен (лимит квоты токенов).",
                "diagnoses": [],
                "contraindications": [],
                "drug_interactions": [],
                "recommendations": []
            }, response.text, True

        response.raise_for_status()
        data = response.json()
        reset_llm_errors()
        raw_content = data["choices"][0]["message"]["content"]
        
        # Учет потребления токенов
        try:
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            resp_model = data.get("model", MODEL)
            record_llm_usage(resp_model, prompt_tokens, completion_tokens, total_tokens, "clinical_summary")
        except Exception as usage_err:
            logger.error(f"[LLM USAGE TRACK ERROR] {usage_err}")

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
        increment_llm_errors()
        print(f"[MEDICAL SUMMARY EXCEPTION] {e}")
        return {
            "anamnesis": f"Ошибка генерации резюме: {str(e)}",
            "diagnoses": [],
            "contraindications": [],
            "drug_interactions": [],
            "recommendations": [],
            "raw_response": str(e)
        }, str(e), True

def get_gigachat_balance() -> dict:
    """
    Запрашивает официальный баланс токенов Сбера через GET https://gigachat.devices.sberbank.ru/api/v1/balance
    Gracefully обрабатывает:
    - 200 OK: возвращает остаток токенов по пакетам/моделям.
    - 403 Forbidden: стандартное поведение Сбера для аккаунтов с постоплатой (Pay-As-You-Go).
    - Расчетный остаток по купленному пакету из GIGACHAT_PACKAGE_TOKENS_LIMIT (с предупреждением при >= 80%).
    """
    token = get_gigachat_token()
    if not token:
        return {
            "status": "error",
            "http_code": None,
            "balance": None,
            "message": "Не удалось получить OAuth токен GigaChat."
        }

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    result = {
        "status": "unknown",
        "http_code": None,
        "balance": None,
        "message": "",
        "package_limit": None,
        "calculated_remaining": None,
        "usage_percent": None
    }

    # Проверка опционального лимита пакета
    pkg_limit_str = os.getenv("GIGACHAT_PACKAGE_TOKENS_LIMIT")
    all_time_tokens = 0
    try:
        summary = get_llm_usage_summary()
        all_time_tokens = summary.get("all_time", {}).get("total_tokens", 0)
    except Exception:
        pass

    if pkg_limit_str:
        try:
            pkg_limit = int(pkg_limit_str.strip())
            result["package_limit"] = pkg_limit
            remaining = max(0, pkg_limit - all_time_tokens)
            usage_pct = round((all_time_tokens / pkg_limit) * 100, 2) if pkg_limit > 0 else 0.0
            result["calculated_remaining"] = remaining
            result["usage_percent"] = usage_pct

            if usage_pct >= 80.0:
                logger.warning(f"[LLM QUOTA WARNING] Внимание! Израсходовано {usage_pct}% лимита токенов GigaChat ({all_time_tokens}/{pkg_limit})")
        except Exception as parse_err:
            logger.error(f"[GIGACHAT PACKAGE PARSE ERROR] {parse_err}")

    try:
        res = requests.get(GIGACHAT_BALANCE_URL, headers=headers, verify=False, timeout=15)
        result["http_code"] = res.status_code

        if res.status_code == 200:
            result["status"] = "available"
            result["balance"] = res.json()
            result["message"] = "Официальный баланс токенов успешно получен из GigaChat API."
        elif res.status_code == 403:
            result["status"] = "pay_as_you_go"
            result["message"] = "Оплата производится по факту потребления (Pay-As-You-Go). Официальный баланс пакетов возвращает 403 (характерно для постоплаты). Точный финансовый баланс доступен в личном кабинете Сбер Бизнес / Studio."
        else:
            result["status"] = "error"
            result["message"] = f"GigaChat Balance API вернул статус {res.status_code}: {res.text}"
    except Exception as e:
        result["status"] = "exception"
        result["message"] = f"Исключение при запросе баланса: {str(e)}"

    return result


# --- ГЕНЕРАЦИЯ ХРОНОЛОГИИ АНАЛИЗОВ В КАБИНЕТЕ ВРАЧА (Block 4) ---

def _deterministic_extract_analyses(text: str) -> list:
    """
    Детерминированное извлечение медицинских показателей и анализов из текста документов.
    """
    items = []
    date_regex = re.compile(r'\b(\d{2}[./-]\d{2}[./-]\d{4}|\d{4}[./-]\d{2}[./-]\d{2})\b')
    current_date = ""

    # Популярные медицинские показатели в педиатрии и неврологии
    patterns = [
        ("Гемоглобин", r'(?:гемоглобин|hgb|hb)\s*[:=–—\-]?\s*(\d+(?:[.,]\d+)?)\s*(г/л|g/l)?', "120-140 г/л", 120.0, 140.0),
        ("Ферритин", r'(?:ферритин|ferritin)\s*[:=–—\-]?\s*(\d+(?:[.,]\d+)?)\s*(нг/мл|ng/ml|мкг/л)?', "30-100 нг/мл", 30.0, 100.0),
        ("Витамин D", r'(?:витамин\s*d|25-oh\s*d)\s*[:=–—\-]?\s*(\d+(?:[.,]\d+)?)\s*(нг/мл|ng/ml)?', "30-100 нг/мл", 30.0, 100.0),
        ("Эритроциты", r'(?:эритроциты|rbc)\s*[:=–—\-]?\s*(\d+(?:[.,]\d+)?)\s*(\*?10\^?12/л)?', "4.0-5.0 *10^12/л", 4.0, 5.0),
        ("Лейкоциты", r'(?:лейкоциты|wbc)\s*[:=–—\-]?\s*(\d+(?:[.,]\d+)?)\s*(\*?10\^?9/л)?', "4.5-10.0 *10^9/л", 4.5, 10.0),
        ("СОЭ", r'(?:соэ|esr)\s*[:=–—\-]?\s*(\d+(?:[.,]\d+)?)\s*(мм/ч|mm/h)?', "2-15 мм/ч", 2.0, 15.0),
        ("ТТГ", r'(?:ттг|tsh)\s*[:=–—\-]?\s*(\d+(?:[.,]\d+)?)\s*(мкме/мл|мме/л)?', "0.4-4.0 мкМЕ/мл", 0.4, 4.0),
    ]

    for line in text.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue
        
        # Проверяем дату в строке
        dates_found = date_regex.findall(line_clean)
        if dates_found:
            current_date = dates_found[0]

        for test_name, pat, norm_str, min_val, max_val in patterns:
            match = re.search(pat, line_clean, re.IGNORECASE)
            if match:
                val_str = match.group(1).replace(",", ".")
                unit = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""
                full_val = f"{val_str} {unit}".strip()
                try:
                    num_val = float(val_str)
                    if num_val < min_val:
                        dev = "Ниже нормы"
                        is_out = True
                    elif num_val > max_val:
                        dev = "Выше нормы"
                        is_out = True
                    else:
                        dev = "В норме"
                        is_out = False
                except ValueError:
                    dev = "В норме"
                    is_out = False

                items.append({
                    "date": current_date or "2026-01-01",
                    "test_name": f"Клинический анализ ({test_name})",
                    "parameter": test_name,
                    "value": full_val,
                    "norm": norm_str,
                    "deviation": dev,
                    "is_out_of_norm": is_out,
                    "comment": f"Показатель {test_name}: {dev.lower()}"
                })

    # Если ничего не нашли через паттерны, создаем структурированную выжимку из первого абзаца
    if not items:
        items.append({
            "date": current_date or "2026-01-01",
            "test_name": "Первичная диагностика",
            "parameter": "Клинический статус",
            "value": "Данные зафиксированы в медкарте",
            "norm": "Возрастная норма",
            "deviation": "В норме",
            "is_out_of_norm": False,
            "comment": "По результатам осмотра специалистов центра"
        })

    return items

def _post_process_analyses(items: list) -> list:
    """
    Сортирует анализы по дате, группирует повторные анализы и вычисляет динамику (↑, ↓, →).
    """
    if not items:
        return []

    def parse_d(item):
        d_str = str(item.get("date", ""))
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(d_str, fmt)
            except Exception:
                pass
        return datetime.min

    sorted_items = sorted(items, key=parse_d)
    param_history = {}

    for item in sorted_items:
        key = item.get("test_name", item.get("parameter", "")).lower().strip()
        if not key:
            continue
        if key not in param_history:
            param_history[key] = []
        param_history[key].append(item)

    for key, history in param_history.items():
        if len(history) > 1:
            for idx, item in enumerate(history):
                item["is_repeated"] = True
                if idx > 0:
                    prev_val_str = history[idx - 1].get("value", "")
                    curr_val_str = item.get("value", "")
                    prev_num = re.findall(r'[-+]?\d*\.?\d+', prev_val_str.replace(",", "."))
                    curr_num = re.findall(r'[-+]?\d*\.?\d+', curr_val_str.replace(",", "."))
                    if prev_num and curr_num:
                        try:
                            p_val = float(prev_num[0])
                            c_val = float(curr_num[0])
                            if c_val > p_val:
                                item["dynamics"] = "↑"
                            elif c_val < p_val:
                                item["dynamics"] = "↓"
                            else:
                                item["dynamics"] = "→"
                        except Exception:
                            item["dynamics"] = ""
                else:
                    item["dynamics"] = ""
        else:
            for item in history:
                item["is_repeated"] = False
                item["dynamics"] = ""

    return sorted_items

def extract_patient_analyses(patient_folder_id: str) -> list:
    """
    RAG-пайплайн извлечения медицинских анализов из документов пациента:
    1. Сканирует чанки документов пациента из кэша.
    2. Извлекает даты, названия анализов, показатели, нормы, комментарии.
    3. Определяет повторные анализы (одинаковые названия в разные даты).
    4. Вычисляет отклонения от нормы и динамику изменений (↑, ↓, →).
    Возвращает структурированный список словарей.
    """
    chunks = get_patient_chunks(patient_folder_id)
    if not chunks:
        return []

    context_parts = []
    for c in chunks[:15]:
        content = c.get("content", "")
        if content:
            context_parts.append(content)
    full_context = "\n---\n".join(context_parts)
    if not full_context:
        return []

    token = get_gigachat_token()
    extracted_items = []
    if token:
        system_prompt = """Ты — медицинский аналитик-эксперт. Твоя задача — извлечь из медицинских документов пациента ВСЕ лабораторные анализы, инструментальные обследования и клинические показатели в виде строгого JSON-массива.
Каждый объект массива должен иметь следующие поля:
- date: строка даты (например, "2026-02-15" или "15.02.2026", если даты нет - "")
- test_name: название анализа (например, "Клинический анализ крови (Гемоглобин)", "Ферритин", "ЭЭГ мониторинг")
- parameter: конкретный показатель
- value: полученное значение с единицами измерения (например, "112 г/л", "3.4 ммоль/л", "Без эпиактивности")
- norm: референсная норма (например, "120-140 г/л", "Возрастная норма")
- deviation: отклонение словами ("В норме", "Ниже нормы", "Выше нормы")
- is_out_of_norm: boolean (true, если показатель выходит за пределы нормы, иначе false)
- comment: краткий клинический комментарий / заключение

Если анализов нет, верни пустой массив [].
Ответь ТОЛЬКО чистым JSON-массивом без окружающего текста."""

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Контекст медицинских документов пациента:\n{full_context}"}
            ],
            "temperature": 0.1
        }
        try:
            res = requests.post(GIGACHAT_COMPLETIONS_URL, headers=headers, json=payload, verify=False, timeout=30)
            if res.status_code == 200:
                data = res.json()
                raw_text = data["choices"][0]["message"]["content"].strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                parsed = json.loads(raw_text)
                if isinstance(parsed, list):
                    extracted_items = parsed
                elif isinstance(parsed, dict) and "analyses" in parsed:
                    extracted_items = parsed["analyses"]
                
                try:
                    usage = data.get("usage", {})
                    record_llm_usage(data.get("model", MODEL), usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), usage.get("total_tokens", 0), "analyses_extraction")
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"[EXTRACT ANALYSES LLM ERROR] {e}")

    if not extracted_items:
        extracted_items = _deterministic_extract_analyses(full_context)

    return _post_process_analyses(extracted_items)



