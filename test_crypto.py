import os
from crypto_utils import encrypt_text, decrypt_text, generate_key

def test_crypto_roundtrip():
    # Убедимся, что у нас есть ключ для теста
    if not os.getenv("ENCRYPTION_KEY"):
        os.environ["ENCRYPTION_KEY"] = generate_key()
        
    original_text = "Секретный диагноз пациента: ОРВИ"
    encrypted = encrypt_text(original_text)
    
    assert encrypted != original_text
    assert encrypted != ""
    
    decrypted = decrypt_text(encrypted)
    assert decrypted == original_text
    print("Тест Roundtrip успешно пройден.")

def test_empty_values():
    assert encrypt_text("") == ""
    assert encrypt_text(None) == ""
    assert decrypt_text("") == ""
    assert decrypt_text(None) == ""
    print("Тест пустых значений успешно пройден.")

def test_graceful_degradation():
    unencrypted_data = "Старые данные в БД"
    # Пытаемся расшифровать невалидный токен
    result = decrypt_text(unencrypted_data)
    assert result == unencrypted_data
    print("Тест Graceful Degradation успешно пройден.")

if __name__ == "__main__":
    test_crypto_roundtrip()
    test_empty_values()
    test_graceful_degradation()
    print("Все тесты модуля шифрования успешно пройдены!")
