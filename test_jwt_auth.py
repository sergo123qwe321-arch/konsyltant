from datetime import timedelta
import time
from fastapi.testclient import TestClient
from main import app
from database import create_patient_access, init_db
from security_utils import create_access_token, verify_token

client = TestClient(app)

def test_jwt_token_generation_and_verification():
    print("\n--- Тест JWT: Генерация и валидация токена ---")
    data = {"sub": "patient_token_123", "allowed_folder": "folder_abc_456"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)
    
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "patient_token_123"
    assert payload["allowed_folder"] == "folder_abc_456"
    assert "exp" in payload
    print("[OK] Токен успешно создан и верифицирован:", payload)

def test_jwt_token_expiration():
    print("\n--- Тест JWT: Истечение срока жизни (30 минут / просроченный токен) ---")
    data = {"sub": "patient_token_expired", "allowed_folder": "folder_expired"}
    # Создаем токен с уже истекшим сроком (отрицательный delta)
    expired_token = create_access_token(data, expires_delta=timedelta(seconds=-10))
    
    payload = verify_token(expired_token)
    assert payload is None, "Просроченный токен не должен проходить валидацию"
    print("[OK] Просроченный токен успешно отклонен verify_token.")

def test_jwt_invalid_token():
    print("\n--- Тест JWT: Невалидный или поврежденный токен ---")
    assert verify_token("invalid.token.string") is None
    assert verify_token("") is None
    assert verify_token(None) is None
    print("[OK] Невалидный токен возвращает None.")

def test_protected_routes_with_jwt():
    print("\n--- Тест JWT: Защищенные роуты API ---")
    init_db()
    password = "JwtTestPassword123!"
    folder_id = "test_folder_jwt_789"
    patient_token = create_patient_access(password, folder_id)
    
    # 1. Логин и получение JWT
    res_login = client.post("/api/login", json={"token": patient_token, "password": password})
    assert res_login.status_code == 200
    res_json = res_login.json()
    assert "access_token" in res_json
    assert "session_token" in res_json
    jwt_token = res_json["access_token"]
    
    # 2. Запрос без токена -> 401
    res_no_auth = client.get("/api/patient/files")
    assert res_no_auth.status_code == 401
    print("[OK] Запрос без заголовка Authorization отклонен (401)")
    
    # 3. Запрос с невалидным токеном -> 401
    res_bad_auth = client.get("/api/patient/files", headers={"Authorization": "Bearer fake_invalid_jwt"})
    assert res_bad_auth.status_code == 401
    print("[OK] Запрос с невалидным токеном отклонен (401)")
    
    # 4. Запрос с просроченным токеном -> 401
    expired_jwt = create_access_token({"sub": patient_token, "allowed_folder": folder_id}, expires_delta=timedelta(seconds=-5))
    res_expired = client.get("/api/patient/files", headers={"Authorization": f"Bearer {expired_jwt}"})
    assert res_expired.status_code == 401
    print("[OK] Запрос с просроченным токеном отклонен (401)")
    
    # 5. Запрос с валидным JWT в /api/chat
    res_chat = client.post("/api/chat", 
                           headers={"Authorization": f"Bearer {jwt_token}"},
                           json={"message": "Привет!"})
    # Чат возвращает 200 (или ответ RAG)
    assert res_chat.status_code == 200
    print(f"[OK] Запрос в /api/chat с валидным JWT успешен (200): {res_chat.json()}")

if __name__ == "__main__":
    test_jwt_token_generation_and_verification()
    test_jwt_token_expiration()
    test_jwt_invalid_token()
    test_protected_routes_with_jwt()
    print("\n[+] ВСЕ ТЕСТЫ БЕЗОПАСНОСТИ JWT УСПЕШНО ПРОЙДЕНЫ!")
