# -*- coding: utf-8 -*-
from fastapi.testclient import TestClient
from main import app
from database import init_db

client = TestClient(app)

def test_cms_and_public():
    init_db()
    
    print("\n--- 1. Тест публичных сервисов, докторов и статей ---")
    res_srv = client.get("/api/v1/public/services")
    assert res_srv.status_code == 200
    services = res_srv.json()
    assert len(services) >= 3
    print(f"[OK] Услуги загружены: {len(services)} шт.")

    res_doc = client.get("/api/v1/public/doctors")
    assert res_doc.status_code == 200
    doctors = res_doc.json()
    assert len(doctors) >= 3
    print(f"[OK] Доктора загружены: {len(doctors)} чел.")

    res_posts = client.get("/api/v1/public/posts")
    assert res_posts.status_code == 200
    posts = res_posts.json()
    assert len(posts) >= 3
    print(f"[OK] Экспертные статьи загружены: {len(posts)} шт.")
    
    first_post_id = posts[0]["id"]
    res_single = client.get(f"/api/v1/public/posts/{first_post_id}")
    assert res_single.status_code == 200
    assert "content" in res_single.json()
    print(f"[OK] Детали статьи ID={first_post_id} получены.")

    print("\n--- 2. Тест отправки заявки родителя (Lead) ---")
    lead_data = {
        "name": "Елена Тестовая",
        "phone": "+7 (999) 777-66-55",
        "child_age": "Логопедия",
        "message": "Ребенку 4 года, хотим прийти на консультацию"
    }
    res_lead = client.post("/api/v1/public/leads", json=lead_data)
    assert res_lead.status_code == 200
    assert res_lead.json()["status"] == "ok"
    print("[OK] Заявка успешно принята через публичный эндпоинт.")

    print("\n--- 3. Тест авторизации Администратора CMS ---")
    res_bad_login = client.post("/api/v1/admin/login", json={"username": "admin", "password": "wrongpassword"})
    assert res_bad_login.status_code == 401
    print("[OK] Неверный пароль админа отклонен (401).")

    res_login = client.post("/api/v1/admin/login", json={"username": "admin", "password": "admin123"})
    assert res_login.status_code == 200
    admin_token = res_login.json()["access_token"]
    assert admin_token
    print(f"[OK] Администратор успешно вошел, получен токен: {admin_token[:15]}...")

    headers = {"Authorization": f"Bearer {admin_token}"}

    print("\n--- 4. Тест получения списка заявок администратором ---")
    res_leads = client.get("/api/v1/admin/leads", headers=headers)
    assert res_leads.status_code == 200
    leads_list = res_leads.json()
    assert len(leads_list) >= 1
    assert leads_list[0]["phone"] == "+7 (999) 777-66-55"
    print(f"[OK] Список заявок получен в CMS: найдено {len(leads_list)} заявок.")

    print("\n--- 5. Тест создания, редактирования и удаления статьи в CMS ---")
    new_post = {
        "title": "Тестовая статья от CMS",
        "summary": "Анонс новой тестовой публикации",
        "content": "Полный текст тестовой статьи для проверки CRUD операций.",
        "tags": ["Тест", "Развитие"]
    }
    res_create = client.post("/api/v1/admin/posts", json=new_post, headers=headers)
    assert res_create.status_code == 200
    print("[OK] Статья создана через CMS.")

    all_posts = client.get("/api/v1/public/posts").json()
    created_post = [p for p in all_posts if p["title"] == "Тестовая статья от CMS"][0]
    created_id = created_post["id"]

    updated_post = {
        "title": "Обновленная статья от CMS",
        "summary": "Обновленный анонс",
        "content": "Обновленный текст статьи.",
        "tags": ["Обновлено"]
    }
    res_update = client.put(f"/api/v1/admin/posts/{created_id}", json=updated_post, headers=headers)
    assert res_update.status_code == 200
    print(f"[OK] Статья ID={created_id} успешно обновлена.")

    res_del = client.delete(f"/api/v1/admin/posts/{created_id}", headers=headers)
    assert res_del.status_code == 200
    print(f"[OK] Статья ID={created_id} успешно удалена.")

    print("\n--- 6. Тест защиты административных эндпоинтов от неавторизованных запросов ---")
    res_unauth = client.get("/api/v1/admin/leads")
    assert res_unauth.status_code == 401
    print("[OK] Доступ к заявкам без токена заблокирован (401).")

    print("\n[+] ВСЕ ТЕСТЫ ПУБЛИЧНОГО ЛЕНДИНГА И АДМИН-ПАНЕЛИ CMS ПРОЙДЕНЫ УСПЕШНО!")

if __name__ == "__main__":
    test_cms_and_public()
