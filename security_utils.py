import os
import re
import urllib.parse
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError, ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "temporary-default-jwt-secret-key-change-me"))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает подписанный JWT токен доступа (Stateless Session).
    В payload сохраняются:
      - sub: идентификатор / токен пациента
      - allowed_folder: привязанная защищенная папка
      - exp: время истечения срока действия (по умолчанию 30 минут)
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Валидирует JWT токен, проверяет цифровую подпись и срок годности (exp).
    Возвращает расшифрованный payload (dict) в случае успеха,
    либо None, если токен просрочен, подпись неверна или структура повреждена.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        logger.warning("[JWT AUTH] Срок действия токена истек (ExpiredSignatureError).")
        return None
    except InvalidTokenError as e:
        logger.warning(f"[JWT AUTH] Невалидный токен (InvalidTokenError): {e}")
        return None
    except PyJWTError as e:
        logger.error(f"[JWT AUTH] Ошибка декодирования JWT: {e}")
        return None
    except Exception as e:
        logger.error(f"[JWT AUTH] Непредвиденная ошибка при проверке токена: {e}")
        return None

def mask_credential(value: str) -> str:
    """
    Маскирует чувствительные данные (Data Redaction / Obfuscation).
    Паттерн обфускации: оставляет первые 3 и последние 3 символа (abc...xyz).
    Если длина <= 6, оставляет первый и последний символ (a***z).
    """
    if not value:
        return ""
    val_str = str(value).strip()
    length = len(val_str)
    if length <= 2:
        return "***"
    elif length <= 6:
        return f"{val_str[0]}***{val_str[-1]}"
    return f"{val_str[:3]}...{val_str[-3:]}"

def mask_url(url: str) -> str:
    """
    Маскирует значение токена авторизации в URL адресе.
    """
    if not url:
        return ""
    if "?token=" in url:
        parts = url.split("?token=", 1)
        token_part = parts[1]
        # Если есть дополнительные query-параметры
        if "&" in token_part:
            t_val, rest = token_part.split("&", 1)
            return f"{parts[0]}?token={mask_credential(t_val)}&{rest}"
        return f"{parts[0]}?token={mask_credential(token_part)}"
    return url

def mask_ip(ip: str) -> str:
    """
    Маскирует IP-адрес для безопасного логирования (CWE-532).
    Пример: '192.168.1.100' -> '192.***.***.100'
    '127.0.0.1' -> '127.***.***.1'
    """
    if not ip:
        return "unknown"
    val = str(ip).strip()
    if val in ("unknown", "testclient"):
        return val
    parts = val.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.***.***.{parts[3]}"
    if ":" in val:
        colon_parts = val.split(":")
        if len(colon_parts) > 2:
            return f"{colon_parts[0]}:***:***:{colon_parts[-1]}"
    return mask_credential(val)

import time
import threading
from typing import List, Tuple

class InMemoryAuthRateLimiter:
    """
    In-memory Rate Limiter для endpoints авторизации с защитой от brute-force атак.
    
    Лимиты:
      - Максимум: 5 запросов в течение скользящего окна 60 секунд.
      - Блокировка: 300 секунд (5 минут) при превышении лимита.
      - Сброс: при успешной авторизации (HTTP 200).
    """
    def __init__(self, max_requests: int = 5, window_seconds: int = 60, lockout_seconds: int = 300):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        self._lock = threading.Lock()
        self.attempts: Dict[str, List[float]] = {}
        self.lockouts: Dict[str, float] = {}

    def is_rate_limited(self, ip: str, path: str = "") -> Tuple[bool, int, int]:
        """
        Проверяет, заблокирован ли IP-адрес.
        Возвращает кортеж: (is_limited: bool, retry_after: int, current_attempts: int).
        """
        now = time.time()
        with self._lock:
            # 1. Проверяем активную блокировку
            if ip in self.lockouts:
                lock_exp = self.lockouts[ip]
                if now < lock_exp:
                    retry_after = int(lock_exp - now) + 1
                    attempts_count = len(self.attempts.get(ip, []))
                    return True, max(1, retry_after), max(attempts_count, self.max_requests)
                else:
                    del self.lockouts[ip]
                    self.attempts[ip] = []

            # 2. Очищаем старые попытки за пределами окна
            if ip in self.attempts:
                self.attempts[ip] = [t for t in self.attempts[ip] if now - t < self.window_seconds]
                if len(self.attempts[ip]) >= self.max_requests:
                    self.lockouts[ip] = now + self.lockout_seconds
                    return True, self.lockout_seconds, len(self.attempts[ip])

            attempts_count = len(self.attempts.get(ip, []))
            return False, 0, attempts_count

    def record_attempt(self, ip: str, path: str = "") -> int:
        """
        Фиксирует попытку запроса для данного IP.
        Возвращает текущее количество попыток в окне.
        """
        now = time.time()
        with self._lock:
            if ip not in self.attempts:
                self.attempts[ip] = []
            self.attempts[ip] = [t for t in self.attempts[ip] if now - t < self.window_seconds]
            self.attempts[ip].append(now)
            count = len(self.attempts[ip])
            if count >= self.max_requests:
                self.lockouts[ip] = now + self.lockout_seconds
            return count

    def reset(self, ip: str, path: str = "") -> None:
        """
        Сбрасывает счетчик попыток и блокировку (например, при успешной авторизации).
        """
        with self._lock:
            self.attempts.pop(ip, None)
            self.lockouts.pop(ip, None)

    def clear_all(self) -> None:
        """Очищает все счетчики и блокировки (для тестирования)."""
        with self._lock:
            self.attempts.clear()
            self.lockouts.clear()

# --- МОДЕРАЦИЯ И БЕЗОПАСНОСТЬ ОТКРЫТОГО ЧАТА (Block 3) ---

PROFANITY_WORDS_LIST = [
    # Базовые нецензурные корни и словоформы
    r'\bху[йияеёю]\w*',
    r'\bпизд\w*',
    r'\b[её]б[а-яё]*\w*',
    r'\bбля[тд]\w*',
    r'\bсук[а-яё]*\b',
    r'\bмуда[кч]\w*',
    r'\bгондон\w*',
    r'\bшлюх\w*',
    r'\bпид[оа]р\w*',
    r'\bзалуп\w*',
    r'\bу[её]б\w*',
    r'\bдолбо[её]б\w*',
    r'\bчмо\b',
    r'\bмраз[ь|и|ей]\w*',
    r'\bговн\w*',
    r'\bсволоч\w*',
    r'\bдерьм\w*'
]
PROFANITY_REGEX = re.compile('|'.join(PROFANITY_WORDS_LIST), re.IGNORECASE)

ALLOWLIST_VIDEO_DOMAINS = {
    "rutube.ru", "vkvideo.ru", "vk.com", "dzen.ru", "youtube.com", "youtu.be", "video.yandex.ru"
}
ALLOWLIST_IMAGE_DOMAINS = {
    "yandex.ru", "images.yandex.ru", "avatars.mds.yandex.net", "vk.com", "pikabu.ru", "imgur.com", "ibb.co", "i.ibb.co"
}
ALL_ALLOWLIST_DOMAINS = ALLOWLIST_VIDEO_DOMAINS | ALLOWLIST_IMAGE_DOMAINS

BLOCKED_SHORTENERS = {
    "bit.ly", "tinyurl.com", "clck.ru", "goo.gl", "t.co", "is.gd", "cutt.ly"
}
DANGEROUS_SCHEMES = ("javascript:", "data:", "vbscript:", "file:")

URL_PATTERN = re.compile(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(?:\+7|8)[\s\-\(]*\d{3}[\s\-\)]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}')

def contains_profanity(text: str) -> bool:
    """
    Проверяет текст на наличие нецензурной лексики и оскорблений.
    Возвращает True, если найдено запрещенное слово.
    """
    if not text:
        return False
    return bool(PROFANITY_REGEX.search(text))

def extract_domain(url: str) -> str:
    """Извлекает нормализованный домен из URL."""
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def validate_media_url(url: str, media_type: str = "image") -> tuple:
    """
    Валидирует внешний медиа URL (для постов, статей библиотеки и медиа-блоков).
    Возвращает (is_valid, error_detail).
    """
    if not url:
        return False, "URL не может быть пустым"
    
    url_lower = url.lower().strip()
    for scheme in DANGEROUS_SCHEMES:
        if url_lower.startswith(scheme):
            return False, "Использование опасных схем URL запрещено"
            
    domain = extract_domain(url)
    if domain in BLOCKED_SHORTENERS:
        return False, "Использование сервисов сокращения ссылок запрещено"
        
    if media_type == "video":
        if any(domain == d or domain.endswith("." + d) for d in ALLOWLIST_VIDEO_DOMAINS):
            return True, ""
        # Разрешаем также прямые видеофайлы (.mp4, .webm)
        if url_lower.endswith((".mp4", ".webm")):
            return True, ""
        return False, "Видео ссылка должна принадлежать Rutube, VK Video, YouTube, Dzen или Яндекс.Видео"
    else:
        if any(domain == d or domain.endswith("." + d) for d in ALLOWLIST_IMAGE_DOMAINS):
            return True, ""
        # Разрешаем прямые ссылки на изображения
        if any(url_lower.split("?")[0].endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg")):
            return True, ""
        return False, "Ссылка на изображение должна быть из доверенного источника или иметь расширение изображения (.jpg, .png, .webp)"

def process_chat_message_moderation(text: str) -> tuple:
    """
    Анализирует текст сообщения открытого чата:
    1. Проверяет мат-фильтр -> если мат, выбрасывает ValueError.
    2. Проверяет опасные схемы и короткие ссылки -> если есть, выбрасывает ValueError.
    3. Проверяет внешние ссылки:
       - Если все ссылки входят в allowlist -> is_approved = True.
       - Если есть ссылка не из allowlist -> is_approved = False, заменяет ссылку на [ссылка ожидает проверки модератором].
    Возвращает (sanitized_text, is_approved).
    """
    if not text:
        return text, True

    if contains_profanity(text):
        raise ValueError("Сообщение содержит недопустимую лексику. Пожалуйста, соблюдайте правила общения")

    text_lower = text.lower()
    for scheme in DANGEROUS_SCHEMES:
        if scheme in text_lower:
            raise ValueError("Сообщение содержит запрещенную схему URL")

    # Ищем все URL в тексте
    found_urls = URL_PATTERN.findall(text)
    is_approved = True
    processed_text = text

    for raw_url in found_urls:
        domain = extract_domain(raw_url)
        if domain in BLOCKED_SHORTENERS:
            raise ValueError("Использование сокращенных ссылок запрещено правилами безопасности")
            
        # Проверяем, входит ли в белые списки
        in_allowlist = any(domain == d or domain.endswith("." + d) for d in ALL_ALLOWLIST_DOMAINS)
        if not in_allowlist:
            is_approved = False
            processed_text = processed_text.replace(raw_url, "[ссылка ожидает проверки модератором]")

    return processed_text, is_approved


