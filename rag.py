import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from drive_api import get_drive_service, download_file
from document_parser import extract_text

# Настройка OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"

# Триггеры для маршрутизации
TRIGGERS = {
    "анализ крови": ["кров", "гемоглобин", "лейкоциты", "эритроциты", "тромбоциты"],
    "мрт": ["мрт", "томография", "снимок", "головн"],
    "рецепты": ["рецепт", "назначение", "лекарств", "препарат"],
}

SYSTEM_PROMPT_TEMPLATE = """
Ты — ИИ-Консультант, виртуальный помощник пациента.
Твоя задача — отвечать на вопросы пациента, опираясь ИСКЛЮЧИТЕЛЬНО на предоставленный ниже контекст из его медицинских документов.

ЖЕСТКОЕ ПРАВИЛО (ZERO-HALLUCINATION):
1. Ты ОБЯЗАН отвечать только на основе фактов из предоставленных документов.
2. Если в документах нет информации, достаточной для ответа, ты должен прямо ответить: "Извините, но в ваших документах нет информации об этом." Никаких догадок и выдумок!
3. Ты не даешь самостоятельных медицинских советов, а только цитируешь и объясняешь данные из документов.

КОНТЕКСТ ДОКУМЕНТОВ:
{context}
"""

def detect_relevant_files(user_message: str, files: list) -> list:
    """
    Маршрутизация по триггерам. 
    Ищет вхождения триггеров в запрос. Если находит — пытается отфильтровать файлы, 
    содержащие эти триггеры в названии. Иначе возвращает все файлы папки.
    """
    msg_lower = user_message.lower()
    matched_categories = []
    
    for category, keywords in TRIGGERS.items():
        if any(kw in msg_lower for kw in keywords):
            matched_categories.append(category)
            
    if matched_categories:
        relevant = []
        for f in files:
            fname = f['name'].lower()
            is_match = False
            for cat in matched_categories:
                for kw in TRIGGERS[cat]:
                    if kw in fname:
                        is_match = True
                        break
            if is_match:
                relevant.append(f)
        if relevant:
            return relevant
            
    # Возвращаем все, если триггеры не сработали
    return files

def get_openrouter_session() -> requests.Session:
    """
    Создает и настраивает сессию для запросов к OpenRouter:
    - Retries (повторные попытки при 5xx ошибках)
    - Поддержка прокси из переменных окружения
    """
    session = requests.Session()
    
    # Настраиваем повторные попытки (3 попытки с паузой)
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Настраиваем прокси, если заданы
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    proxies = {}
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    if proxies:
        session.proxies.update(proxies)
        
    return session

def ask_consultant(user_message: str, folder_id: str) -> str:
    """
    1. Ищет файлы
    2. Фильтрует по триггерам
    3. Скачивает и парсит текст
    4. Отправляет промпт в OpenRouter
    """
    if not OPENROUTER_API_KEY:
        return "ВНИМАНИЕ: Не задан OPENROUTER_API_KEY в переменных окружения. ИИ недоступен."
        
    service = get_drive_service()
    if not service:
        return "Ошибка доступа к Google Диску."
        
    # Получаем файлы
    query = f"'{folder_id}' in parents and trashed = false"
    try:
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        all_files = results.get('files', [])
    except Exception as e:
        return f"Связь с Google Drive временно недоступна (таймаут или сбой сети). Пожалуйста, подождите и попробуйте снова. (Детали: {str(e)})"
    
    if not all_files:
        return "В вашей папке пока нет медицинских документов."
        
    relevant_files = detect_relevant_files(user_message, all_files)
    
    # Формируем контекст
    context_parts = []
    for f in relevant_files:
        file_bytes = download_file(f['id'], f['mimeType'])
        if file_bytes:
            text = extract_text(file_bytes, f['mimeType'], f['name'])
            context_parts.append(f"--- Документ: {f['name']} ---\n{text}")
            
    full_context = "\n\n".join(context_parts)
    
    if not full_context.strip():
        return "Не удалось извлечь текст из документов."
    
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=full_context)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://konsyltant.test", 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }
    
    session = get_openrouter_session()
    
    try:
        response = session.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.SSLError as e:
        return "Ошибка безопасного соединения с сервером ИИ (SSL). Возможна блокировка, попробуйте позже или проверьте настройки сети."
    except requests.exceptions.Timeout:
        return "Время ожидания ответа от ИИ истекло. Сервер перегружен, попробуйте еще раз."
    except requests.exceptions.RequestException as e:
        return f"Сетевая ошибка при обращении к ИИ: {str(e)}"
    except Exception as e:
        return f"Непредвиденная ошибка: {str(e)}"
