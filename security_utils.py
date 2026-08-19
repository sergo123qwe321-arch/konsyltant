import os
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

