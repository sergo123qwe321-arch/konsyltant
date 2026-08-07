import os
import uuid
import requests
import urllib3
from dotenv import load_dotenv
from document_parser import parse_document_bytes

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

def fetch_yandex_folder_text(folder_id: str) -> str:
    """
    100% Динамическая выкачка и гибридный OCR-парсинг медицинских файлов (PDF сканы, DOCX, PNG, JPG)
    напрямую с Яндекс.Диска для указанной папки folder_id.
    """
    if not YANDEX_DISK_TOKEN:
        return ""

    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}", "Accept": "application/json"}
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    params = {"path": folder_id, "limit": 100}

    parsed_texts = []
    try:
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 200:
            items = res.json().get("_embedded", {}).get("items", [])
            for item in items:
                if item.get("type") == "file":
                    fname = item.get("name", "")
                    fpath = item.get("path")
                    mime_type = item.get("mime_type", "")
                    
                    # Поддерживаем любые векторные и сканированные документы
                    down_res = requests.get(url, headers=headers, params={"path": fpath}, timeout=10)
                    if down_res.status_code == 200:
                        down_url = down_res.json().get("file")
                        if down_url:
                            file_content = requests.get(down_url, timeout=25).content
                            doc_text = parse_document_bytes(file_content, fname, mime_type)
                            
                            if doc_text and doc_text.strip() and not doc_text.startswith("[Неподдерживаемый"):
                                parsed_texts.append(f"--- Файл: {fname} ---\n{doc_text}")
    except Exception as e:
        print(f"[RAG DYNAMIC YANDEX DISK ERROR] {e}")

    return "\n\n".join(parsed_texts)

def build_patient_context(folder_id: str) -> str:
    """
    Чисто динамический контекст: только реальные документы с Яндекс.Диска.
    """
    dynamic_text = fetch_yandex_folder_text(folder_id)
    if dynamic_text.strip():
        return dynamic_text

    clean_name = folder_id.replace("disk:/", "").strip()
    return (
        f"--- Карта Пациента: {clean_name} ---\n"
        f"В вашей папке '{clean_name}' на Яндекс.Диске пока нет доступных медицинских файлов."
    )

def ask_consultant(user_message: str, folder_id: str) -> str:
    """
    Формирует динамический изолированный контекст из документов конкретной папки folder_id и запрашивает ответ у GigaChat.
    """
    token = get_gigachat_token()
    if not token:
        return "ВНИМАНИЕ: Ошибка авторизации GigaChat (проверьте GIGACHAT_CREDENTIALS в .env)."

    context_text = build_patient_context(folder_id)
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

    try:
        response = requests.post(GIGACHAT_COMPLETIONS_URL, headers=headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.SSLError:
        return "Ошибка SSL-соединения с сервером GigaChat."
    except requests.exceptions.Timeout:
        return "Время ожидания ответа от GigaChat истекло. Попробуйте еще раз."
    except requests.exceptions.RequestException as e:
        return f"Сетевая ошибка при обращении к GigaChat: {str(e)}"
    except Exception as e:
        return f"Непредвиденная ошибка GigaChat: {str(e)}"
