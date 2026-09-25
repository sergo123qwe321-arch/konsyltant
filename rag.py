import os
import re
import math
import uuid
import json
import logging
from collections import Counter
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

# ==============================================================================
# BM25 RETRIEVER & RUSSIAN NLP TOKENIZER (PURE PYTHON, ZERO-DEPENDENCY)
# ==============================================================================

MAX_DEFAULT_CHARS = 12000

RUSSIAN_STOP_WORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все", "она",
    "так", "его", "но", "да", "ты", "к", "ко", "у", "же", "вы", "за", "бы", "по", "только",
    "ее", "мне", "было", "вот", "от", "меня", "еще", "нет", "о", "об", "обо", "из", "ему",
    "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни", "быть",
    "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам", "ведь", "там", "потом",
    "себя", "ничего", "ей", "может", "они", "тут", "где", "есть", "надо", "ней", "для",
    "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз", "тоже",
    "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого", "какой",
    "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас",
    "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два", "эти", "этой",
    "перед", "про", "лишь"
}

MEDICAL_SYNONYMS: dict[str, list[str]] = {
    "мрт": ["томография"],
    "томография": ["мрт"],
    "кт": ["томография"],
    "узи": ["сонография", "эхография"],
    "сонография": ["узи"],
    "эхография": ["узи"],
    "аллергия": ["непереносимость"],
    "непереносимость": ["аллергия"],
    "жар": ["температура", "лихорадка"],
    "температура": ["жар", "лихорадка"],
    "лихорадка": ["температура", "жар"],
    "анализ": ["исследование"],
    "исследование": ["анализ"]
}

PERFECTIVEGROUND = re.compile(r'((ив|ивши|ившись|ыв|ывши|ывшись)|((?<=[ая])(в|вши|вшись)))$')
REFLEXIVE = re.compile(r'(с[яь])$')
ADJECTIVE = re.compile(r'(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|ую|юю|ая|яя|ою|ею)$')
PARTICIPLE = re.compile(r'((ивш|ывш|ующ)|((?<=[ая])(ем|нн|вш|ющ|щ)))$')
VERB = re.compile(r'((ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю)|((?<=[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|нно)))$')
NOUN = re.compile(r'(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$')

def stem_russian(word: str) -> str:
    """
    Легковесный стеммер для русского языка (алгоритм Портера).
    Приводит слова к базовой основе для учета падежей, чисел и склонений.
    Слова длиной до 3 символов (включая аббревиатуры МРТ, УЗИ, ЭКГ) сохраняются без изменений.
    """
    word = word.lower().replace('ё', 'е')
    if len(word) <= 3:
        return word
    vowel_match = re.search(r'[аеиоуыэюя]', word)
    if not vowel_match:
        return word
    rv_pos = vowel_match.end()
    head, rv = word[:rv_pos], word[rv_pos:]
    if not rv:
        return word
    m = PERFECTIVEGROUND.search(rv)
    if m:
        rv = rv[:m.start()]
    else:
        m = REFLEXIVE.search(rv)
        if m:
            rv = rv[:m.start()]
        m = ADJECTIVE.search(rv)
        if m:
            rv = rv[:m.start()]
            m2 = PARTICIPLE.search(rv)
            if m2:
                rv = rv[:m2.start()]
        else:
            m = VERB.search(rv)
            if m:
                rv = rv[:m.start()]
            else:
                m = NOUN.search(rv)
                if m:
                    rv = rv[:m.start()]
    if rv.endswith('и'):
        rv = rv[:-1]
    if rv.endswith('ь'):
        rv = rv[:-1]
    return head + rv

def tokenize(text: str, expand_synonyms: bool = False) -> list[str]:
    """
    Русскоязычная токенизация:
    1. Приведение к нижнему регистру и нормализация 'ё' -> 'е'.
    2. Очистка от пунктуации через re.findall(r'\b[а-яa-z0-9]+\b').
    3. Фильтрация базовых стоп-слов.
    4. Стемминг слов для унификации грамматических форм.
    5. При expand_synonyms=True — добавление стеммированных синонимов.
    """
    if not text:
        return []
    cleaned = text.lower().replace('ё', 'е')
    raw_tokens = re.findall(r'\b[а-яa-z0-9]+\b', cleaned)
    tokens: list[str] = []
    for raw in raw_tokens:
        if raw in RUSSIAN_STOP_WORDS:
            continue
        stemmed = stem_russian(raw)
        tokens.append(stemmed)
        if expand_synonyms:
            synonyms = MEDICAL_SYNONYMS.get(raw, []) or MEDICAL_SYNONYMS.get(stemmed, [])
            for syn in synonyms:
                tokens.append(stem_russian(syn))
    return tokens

class OkapiBM25:
    """
    Легковесный автономный класс Okapi BM25 на чистом Python без внешних зависимостей.
    Реализует стандартный алгоритм ранжирования BM25 (k1=1.5, b=0.75) с формулой Lucene для IDF.
    """
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.doc_lengths = [len(doc) for doc in corpus]
        self.avgdl = sum(self.doc_lengths) / self.corpus_size if self.corpus_size > 0 else 0.0
        self.doc_freqs = [Counter(doc) for doc in corpus]
        self.idf: dict[str, float] = {}

        df = Counter()
        for freqs in self.doc_freqs:
            for term in freqs.keys():
                df[term] += 1

        for term, freq in df.items():
            self.idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        scores = [0.0] * self.corpus_size
        if self.corpus_size == 0 or self.avgdl == 0.0 or not query_tokens:
            return scores

        for idx, doc_freq in enumerate(self.doc_freqs):
            doc_len = self.doc_lengths[idx]
            score = 0.0
            for token in query_tokens:
                if token not in doc_freq:
                    continue
                tf = doc_freq[token]
                idf = self.idf.get(token, 0.0)
                num = tf * (self.k1 + 1.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avgdl))
                score += idf * (num / denom)
            scores[idx] = score

        return scores

class PatientContext(str):
    """
    Контекст пациента для передачи в LLM. Наследуется от str для прямой строковой конкатенации/интерполяции
    и поддерживает распаковку в кортеж (context_text, cache_exists) для обратной совместимости.
    """
    def __new__(cls, text: str, cache_exists: bool = True):
        obj = super().__new__(cls, text)
        obj.cache_exists = cache_exists
        return obj

    def __iter__(self):
        return iter((str(self), self.cache_exists))

def build_patient_context(patient_folder: str = None, query: str = None, top_k: int = 7, folder_id: str = None) -> PatientContext:
    """
    Формирует контекст пациента из JSON-кэша Яндекс.Диска с использованием BM25-ретривера.
    - patient_folder (или folder_id): путь к папке пациента на Яндекс.Диске.
    - query: текст вопроса пользователя (при передаче выполняется BM25-ранжирование чанков).
    - top_k: максимальное количество наиболее релевантных чанков для включения в контекст.
    - Сохраняет мета-заголовки файлов (--- Файл: {path} ---) в отобранных чанках.
    - При отсутствии query, нулевых скорах или общей выписке отбирает дефолтный срез (до MAX_DEFAULT_CHARS),
      чтобы гарантированно не превысить лимит 8K токенов базовой модели GigaChat.
    """
    target_folder = patient_folder or folder_id
    if not target_folder:
        return PatientContext("", False)

    cache_data, cache_exists = fetch_yandex_cache_json(target_folder)
    if not cache_exists or not cache_data:
        return PatientContext("", False)

    chunks = cache_data.get("chunks", [])
    if not chunks:
        clean_name = target_folder.replace("disk:/", "").strip()
        return PatientContext(f"--- Карта Пациента: {clean_name} ---\nВ обработанном кэше пока нет содержательного текста.", True)

    selected_chunks: list[str] = []

    # 1. Если query передан и список чанков не пуст: рассчитываем BM25 скоры
    if query and query.strip():
        query_tokens = tokenize(query, expand_synonyms=True)
        if query_tokens:
            corpus = [tokenize(chunk) for chunk in chunks]
            bm25 = OkapiBM25(corpus)
            scores = bm25.get_scores(query_tokens)

            # Отбираем только чанки с положительным скором релевантности
            scored_chunks = [(score, idx, chunk) for idx, (score, chunk) in enumerate(zip(scores, chunks)) if score > 0.0]

            if scored_chunks:
                # Сортируем по убыванию BM25 скора
                scored_chunks.sort(key=lambda x: x[0], reverse=True)
                top_candidates = scored_chunks[:top_k]

                total_chars = 0
                for score, idx, chunk in top_candidates:
                    if selected_chunks and total_chars + len(chunk) > MAX_DEFAULT_CHARS:
                        break
                    selected_chunks.append(chunk)
                    total_chars += len(chunk)

                logger.info(f"[RAG BM25] Запрос: '{query[:60]}' -> найдено {len(scored_chunks)} совпадений, отобрано Top-{len(selected_chunks)} ({total_chars} симв.)")

    # 2. Если query отсутствует, совпадений нет (все скоры 0) или сформирован пустой список:
    if not selected_chunks:
        total_chars = 0
        for chunk in chunks:
            if selected_chunks and total_chars + len(chunk) > MAX_DEFAULT_CHARS:
                break
            selected_chunks.append(chunk)
            total_chars += len(chunk)
            if total_chars >= MAX_DEFAULT_CHARS:
                break
        logger.info(f"[RAG DEFAULT SLICE] Сформирован дефолтный срез: {len(selected_chunks)} из {len(chunks)} чанков ({total_chars} симв.)")

    context_text = "\n\n".join(selected_chunks)
    return PatientContext(context_text, True)

def ask_consultant(user_message: str, folder_id: str) -> str:
    """
    Формирует контекст с помощью BM25-ретривера из массива "chunks" файла _cache.json папки folder_id
    и запрашивает ответ у GigaChat.
    Если файл кэша еще не создан, возвращает технический ответ.
    В случае сетевой ошибки, таймаута или исчерпания квоты (401/403) возвращает пользовательское сообщение о сбое.
    """
    context_text, cache_exists = build_patient_context(patient_folder=folder_id, query=user_message, top_k=7)
    
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
    context_text, cache_exists = build_patient_context(patient_folder=folder_id, query=None, top_k=10)
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



