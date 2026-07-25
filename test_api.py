from fastapi.testclient import TestClient
from main import app
from database import create_patient_access, init_db

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
    
    print("\n--- Тест 2: /api/login ---")
    res_login = client.post("/api/login", json={"token": token, "password": password})
    print(f"Status: {res_login.status_code}, Body: {res_login.json()}")
    assert res_login.status_code == 200
    session_token = res_login.json()["session_token"]
    
    print("\n--- Тест 2.1: /api/login (неверный пароль) ---")
    res_login_bad = client.post("/api/login", json={"token": token, "password": "wrong"})
    print(f"Status: {res_login_bad.status_code}, Body: {res_login_bad.json()}")
    assert res_login_bad.status_code == 401
    
    print("\n--- Тест 3: /api/patient/files ---")
    headers = {"Authorization": f"Bearer {session_token}"}
    res_files = client.get("/api/patient/files", headers=headers)
    print(f"Status: {res_files.status_code}, Body: {res_files.json()}")
    assert res_files.status_code == 200
    
    print("\n--- Тест 3.1: /api/patient/files (без авторизации) ---")
    res_files_no_auth = client.get("/api/patient/files")
    print(f"Status: {res_files_no_auth.status_code}, Body: {res_files_no_auth.json()}")
    assert res_files_no_auth.status_code == 401
    
    print("\n[+] ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")

if __name__ == "__main__":
    test_api()
