import unittest
from fastapi.testclient import TestClient
import database
from main import app
from security_utils import create_access_token

class TestCommunityChat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.ensure_indexes()
        cls.client = TestClient(app)
        
        cls.admin_token = create_access_token({"sub": "admin", "role": "ADMIN", "full_name": "Главный Врач"})
        cls.doctor_token = create_access_token({"sub": "10", "doctor_id": 10, "role": "DOCTOR", "full_name": "Иванова Анна", "specialty": "Нейропсихолог"})
        cls.patient_token = create_access_token({"sub": "patient_1", "role": "PATIENT", "full_name": "Семья Смирновых", "allowed_folder": "disk:/Смирновы"})

    def test_01_public_feed_open_for_all(self):
        """Чтение ленты чата доступно без авторизации"""
        res = self.client.get("/api/v1/public/chat?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIsInstance(data["messages"], list)

    def test_02_posting_by_all_roles(self):
        """Отправка сообщений разрешена родителям, врачам и администраторам с фиксацией роли"""
        # 1. Родитель
        res_p = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Здравствуйте! Подскажите, со скольки лет вы принимаете деток на диагностику?"},
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )
        self.assertEqual(res_p.status_code, 200)
        msg_p = res_p.json()["message"]
        self.assertEqual(msg_p["author_role"], "PATIENT")
        self.assertEqual(msg_p["author_name"], "Семья Смирновых")

        # 2. Врач
        res_d = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Добрый день! Первичную игровую нейродиагностику мы проводим с 2.5 лет."},
            headers={"Authorization": f"Bearer {self.doctor_token}"}
        )
        self.assertEqual(res_d.status_code, 200)
        msg_d = res_d.json()["message"]
        self.assertEqual(msg_d["author_role"], "DOCTOR")
        self.assertEqual(msg_d["author_name"], "Иванова Анна")

        # 3. Администрация
        res_a = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Уважаемые родители, запись на следующую неделю открыта на сайте!"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res_a.status_code, 200)
        msg_a = res_a.json()["message"]
        self.assertEqual(msg_a["author_role"], "ADMIN")
        self.assertEqual(msg_a["author_name"], "Главный Врач")

    def test_03_guest_post_allowed_and_rate_limited(self):
        """Неавторизованный гость может отправлять сообщения до 3 раз в час с IP-лимитом"""
        from main import guest_chat_rate_limiter
        guest_chat_rate_limiter.reset("guest_chat:testclient")
        
        # 1. Первое сообщение гостя
        res = self.client.post("/api/v1/public/chat", json={"message": "Вопрос от гостя сайта", "author_name": "Елена"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["message"]["author_role"], "GUEST")
        self.assertEqual(res.json()["message"]["author_name"], "Елена")
        
        # 2. Второе и третье сообщения
        self.assertEqual(self.client.post("/api/v1/public/chat", json={"message": "Сообщение 2"}).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/public/chat", json={"message": "Сообщение 3"}).status_code, 200)
        
        # 3. Четвертое сообщение превышает лимит (429)
        res_429 = self.client.post("/api/v1/public/chat", json={"message": "Сообщение 4 (лимит)"})
        self.assertEqual(res_429.status_code, 429)
        self.assertIn("Retry-After", res_429.headers)

    def test_04_admin_moderation_deletion(self):
        """Администратор может удалять сообщения из ленты чата"""
        res = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Тестовое сообщение для модерации"},
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )
        msg_id = res.json()["message"]["id"]

        # Врач не может удалять
        res_doc_del = self.client.delete(f"/api/v1/public/chat/{msg_id}", headers={"Authorization": f"Bearer {self.doctor_token}"})
        self.assertEqual(res_doc_del.status_code, 403)

        # Администратор удаляет
        res_adm_del = self.client.delete(f"/api/v1/public/chat/{msg_id}", headers={"Authorization": f"Bearer {self.admin_token}"})
        self.assertEqual(res_adm_del.status_code, 200)
        self.assertEqual(res_adm_del.json()["deleted_id"], msg_id)

if __name__ == "__main__":
    unittest.main()
