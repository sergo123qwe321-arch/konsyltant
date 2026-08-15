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
