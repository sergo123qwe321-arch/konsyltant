import os
import logging
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def generate_key() -> str:
    """Генерирует новый Fernet ключ. Удобно для создания ключа в .env"""
    return Fernet.generate_key().decode('utf-8')

def _get_fernet() -> Fernet:
    """Инициализирует и возвращает экземпляр Fernet на основе ключа из окружения"""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        logger.warning("[SECURITY WARNING] ENCRYPTION_KEY не найден в переменных окружения! "
                       "Используется временный ключ. Данные, зашифрованные этим ключом, "
                       "будут потеряны после перезапуска сервера. Сгенерируйте ключ через generate_key().")
        key = generate_key()
        os.environ["ENCRYPTION_KEY"] = key # Сохраняем в памяти для текущей сессии
    return Fernet(key.encode('utf-8'))

def encrypt_text(plain_text: str) -> str:
    """
    Шифрует обычный текст.
    Возвращает пустую строку, если на вход подана пустая строка или None.
    """
    if not plain_text:
        return ""
    
    f = _get_fernet()
    try:
        encrypted_bytes = f.encrypt(plain_text.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Ошибка шифрования: {e}")
        return ""

def decrypt_text(cipher_text: str) -> str:
    """
    Дешифрует текст.
    При возникновении InvalidToken возвращает исходный текст (Graceful Degradation),
    предполагая, что это старые незашифрованные данные.
    """
    if not cipher_text:
        return ""
        
    f = _get_fernet()
    try:
        decrypted_bytes = f.decrypt(cipher_text.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except InvalidToken:
        logger.warning("Попытка расшифровать некорректный или незашифрованный токен. Возвращаем исходный текст.")
        return cipher_text
    except Exception as e:
        logger.error(f"Ошибка дешифрования: {e}")
        return cipher_text

# Реэкспорт JWT функций для обратной совместимости модулей безопасности
from security_utils import create_access_token, verify_token
