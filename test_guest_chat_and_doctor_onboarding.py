import unittest
from unittest.mock import patch
import uuid
from fastapi.testclient import TestClient

import database
from main import app, guest_chat_rate_limiter
from security_utils import create_access_token


class TestGuestChatAndDoctorOnboarding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.ensure_indexes()
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({"sub": "admin", "role": "ADMIN", "full_name": "Администратор Клиники"})
        cls.doctor_token = create_access_token({"sub": "15", "doctor_id": 15, "role": "DOCTOR", "full_name": "Д-р Кузнецов", "specialty": "Психотерапевт"})
        cls.patient_token = create_access_token({"sub": "patient_42", "role": "PATIENT", "full_name": "Семья Петровых"})

    def setUp(self):
        # Сброс счетчика гостевого лимитера перед каждым тестом
        guest_chat_rate_limiter.reset("guest_chat:testclient")

    def test_01_guest_chat_message_success(self):
        """Отправка сообщения гостем без авторизации (author_role='GUEST', author_id=None)"""
        # С кастомным именем
        res1 = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Здравствуйте, подскажите стоимость первичного приема?", "author_name": "Светлана"}
        )
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["status"], "ok")
        self.assertEqual(data1["message"]["author_role"], "GUEST")
        self.assertIsNone(data1["message"]["author_id"])
        self.assertEqual(data1["message"]["author_name"], "Светлана")
        self.assertTrue(data1["message"]["is_approved"])

        # Без указания имени (дефолт 'Гость')
        res2 = self.client.post(
            "/api/v1/public/chat",
            json={"message": "И еще один общий вопрос по расписанию филиала."}
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["message"]["author_role"], "GUEST")
        self.assertIsNone(data2["message"]["author_id"])
        self.assertEqual(data2["message"]["author_name"], "Гость")

    def test_02_guest_chat_rate_limiting(self):
        """Ограничение частоты запросов для гостей: 3 сообщения в час, 4-е блокируется (429)"""
        # 1-е сообщение
        res1 = self.client.post("/api/v1/public/chat", json={"message": "Гостевое сообщение 1"})
        self.assertEqual(res1.status_code, 200)

        # 2-е сообщение
        res2 = self.client.post("/api/v1/public/chat", json={"message": "Гостевое сообщение 2"})
        self.assertEqual(res2.status_code, 200)

        # 3-е сообщение
        res3 = self.client.post("/api/v1/public/chat", json={"message": "Гостевое сообщение 3"})
        self.assertEqual(res3.status_code, 200)

        # 4-е сообщение (Превышение лимита 3/час)
        res4 = self.client.post("/api/v1/public/chat", json={"message": "Гостевое сообщение 4"})
        self.assertEqual(res4.status_code, 429)
        self.assertIn("Retry-After", res4.headers)
        self.assertIn("Лимит для гостей", res4.json().get("detail", ""))

    def test_03_authenticated_user_bypasses_guest_limit(self):
        """Авторизованные пользователи не блокируются гостевым лимитером 3 сообщ/час"""
        # Забиваем гостевой лимит до упора (3 штуки)
        for i in range(3):
            self.client.post("/api/v1/public/chat", json={"message": f"Гость исчерпывает квоту #{i+1}"})

        # Проверяем, что гость теперь заблокирован
        res_guest = self.client.post("/api/v1/public/chat", json={"message": "Гость должен получить 429"})
        self.assertEqual(res_guest.status_code, 429)

        # Но авторизованный администратор может отправлять сообщения
        res_admin = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Сообщение от администрации клиники"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.json()["message"]["author_role"], "ADMIN")

        # И авторизованный пациент также может отправлять сообщения
        res_patient = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Сообщение от авторизованного родителя"},
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )
        self.assertEqual(res_patient.status_code, 200)
        self.assertEqual(res_patient.json()["message"]["author_role"], "PATIENT")

    def test_04_guest_chat_profanity_and_url_moderation(self):
        """Проверка фильтрации мата и очереди премодерации ссылок в гостевых сообщениях"""
        # 1. Нецензурная лексика блокируется
        res_bad = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Здесь содержится мат блять в сообщении", "author_name": "Хулиган"}
        )
        self.assertEqual(res_bad.status_code, 400)
        self.assertIn("недопустимую лексику", res_bad.json().get("detail", ""))

        # 2. Сторонняя ссылка отправляется на премодерацию (is_approved=False)
        res_link = self.client.post(
            "/api/v1/public/chat",
            json={"message": "Посмотрите полезный сайт https://external-medical-portal.example.com", "author_name": "Гость"}
        )
        self.assertEqual(res_link.status_code, 200)
        msg_data = res_link.json()["message"]
        self.assertFalse(msg_data["is_approved"])
        self.assertEqual(res_link.json()["status"], "ok")
        self.assertFalse(res_link.json()["is_approved"])

    @patch("main.send_doctor_onboarding_email", return_value=True)
    def test_05_admin_create_doctor_endpoint(self, mock_send_email):
        """Создание врача через POST /api/v1/admin/doctors под администратором"""
        unique_email = f"doc_{uuid.uuid4().hex[:8]}@cmz.site"
        payload = {
            "full_name": "Михайлова Екатерина Сергеевна",
            "specialty": "Детский психиатр, психотерапевт",
            "email": unique_email,
            "phone": "+7 912 345-67-89"
        }

        res = self.client.post(
            "/api/v1/admin/doctors",
            json=payload,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["email_sent"])
        self.assertIn("temporary_password", data)
        self.assertEqual(len(data["temporary_password"]), 12)

        doc = data["doctor"]
        self.assertEqual(doc["full_name"], payload["full_name"])
        self.assertEqual(doc["specialty"], payload["specialty"])
        self.assertEqual(doc["email"], unique_email)
        self.assertTrue(doc["license_number"].startswith("DOC-"))
        self.assertTrue(doc["is_verified"])
        self.assertEqual(doc["role"], "DOCTOR")

        # Проверяем вызов отправки email
        mock_send_email.assert_called_once_with(
            doctor_email=unique_email,
            full_name=payload["full_name"],
            temp_password=data["temporary_password"],
            specialty=payload["specialty"]
        )

        # Проверяем сохранение в БД
        db_doc = database.get_doctor_by_email(unique_email)
        self.assertIsNotNone(db_doc)
        self.assertEqual(db_doc["id"], doc["id"])

        # Проверка защиты от дублирования email
        res_dup = self.client.post(
            "/api/v1/admin/doctors",
            json=payload,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res_dup.status_code, 400)
        self.assertIn("уже зарегистрирован", res_dup.json().get("detail", ""))

    def test_06_admin_create_doctor_unauthorized(self):
        """Защита эндпоинта онбординга: запрет неавторизованным и пользователям без роли ADMIN"""
        payload = {
            "full_name": "Хакер Попытка",
            "specialty": "Взломщик",
            "email": "hacker@evil.com"
        }

        # 1. Без токена (401)
        res_no_auth = self.client.post("/api/v1/admin/doctors", json=payload)
        self.assertEqual(res_no_auth.status_code, 401)

        # 2. С токеном пациента (403)
        res_patient = self.client.post(
            "/api/v1/admin/doctors",
            json=payload,
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )
        self.assertEqual(res_patient.status_code, 403)

        # 3. С токеном врача (403)
        res_doc = self.client.post(
            "/api/v1/admin/doctors",
            json=payload,
            headers={"Authorization": f"Bearer {self.doctor_token}"}
        )
        self.assertEqual(res_doc.status_code, 403)

    def test_07_admin_get_doctors_list(self):
        """Получение реестра врачей через GET /api/v1/admin/doctors с защитой password_hash"""
        res = self.client.get(
            "/api/v1/admin/doctors",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIsInstance(data["doctors"], list)
        self.assertGreater(len(data["doctors"]), 0)

        # Проверяем структуру и отсутствие утечки password_hash
        for doc in data["doctors"]:
            self.assertIn("id", doc)
            self.assertIn("full_name", doc)
            self.assertIn("specialty", doc)
            self.assertIn("license_number", doc)
            self.assertIn("is_verified", doc)
            self.assertIn("created_at", doc)
            self.assertNotIn("password_hash", doc)

        # Без авторизации (401)
        res_unauth = self.client.get("/api/v1/admin/doctors")
        self.assertEqual(res_unauth.status_code, 401)

        # С ролью пациента (403)
        res_forbidden = self.client.get(
            "/api/v1/admin/doctors",
            headers={"Authorization": f"Bearer {self.patient_token}"}
        )
        self.assertEqual(res_forbidden.status_code, 403)


if __name__ == "__main__":
    unittest.main()
