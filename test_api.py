from datetime import timedelta
from fastapi.testclient import TestClient
from main import app
from database import create_patient_access, init_db
from security_utils import create_access_token

client = TestClient(app)

def test_api():
    print("Инициализация БД и создание тестового токена...")
    init_db()
    password = "ApiTestPassword123!"
    folder_id = "1Hs5A-kx0WfoR8vhUX5xX_XqMtVcwgHu6"
    token = create_patient_access(password, folder_id)
    
    print("\n--- Тест 1: /api/verify-token ---")
    res = client.post("/api/verify-token", json={"token": token})
    print(f"Status: {res.status_code}, Body: {res.json()}")
    assert res.status_code == 200
    
    print("\n--- Тест 1.1: /api/verify-token (неверный токен) ---")
    res_bad = client.post("/api/verify-token", json={"token": "bad_token"})
    print(f"Status: {res_bad.status_code}, Body: {res_bad.json()}")
    assert res_bad.status_code == 404
    
    print("\n--- Тест 2: /api/login (генерация JWT) ---")
    res_login = client.post("/api/login", json={"token": token, "password": password})
    print(f"Status: {res_login.status_code}, Body: {res_login.json()}")
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()
    assert "session_token" in res_login.json()
    session_token = res_login.json()["session_token"]
    
    print("\n--- Тест 2.1: /api/login (неверный пароль) ---")
    res_login_bad = client.post("/api/login", json={"token": token, "password": "wrong"})
    print(f"Status: {res_login_bad.status_code}, Body: {res_login_bad.json()}")
    assert res_login_bad.status_code == 401
    
    print("\n--- Тест 3: /api/patient/files (валидный JWT) ---")
    headers = {"Authorization": f"Bearer {session_token}"}
    res_files = client.get("/api/patient/files", headers=headers)
    print(f"Status: {res_files.status_code}, Body: {res_files.json()}")
    assert res_files.status_code == 200
    
    print("\n--- Тест 3.1: /api/patient/files (без авторизации) ---")
    res_files_no_auth = client.get("/api/patient/files")
    print(f"Status: {res_files_no_auth.status_code}, Body: {res_files_no_auth.json()}")
    assert res_files_no_auth.status_code == 401
    
    print("\n--- Тест 3.2: /api/patient/files (просроченный JWT) ---")
    expired_jwt = create_access_token({"sub": token, "allowed_folder": folder_id}, expires_delta=timedelta(seconds=-1))
    res_files_expired = client.get("/api/patient/files", headers={"Authorization": f"Bearer {expired_jwt}"})
    print(f"Status: {res_files_expired.status_code}, Body: {res_files_expired.json()}")
    assert res_files_expired.status_code == 401

    print("\n--- Тест 3.3: /api/patient/files (невалидный/поддельный JWT) ---")
    res_files_tampered = client.get("/api/patient/files", headers={"Authorization": "Bearer fake.tampered.token"})
    print(f"Status: {res_files_tampered.status_code}, Body: {res_files_tampered.json()}")
    assert res_files_tampered.status_code == 401
    
    print("\n[+] ВСЕ ТЕСТЫ API И JWT УСПЕШНО ПРОЙДЕНЫ!")

if __name__ == "__main__":
    test_api()
