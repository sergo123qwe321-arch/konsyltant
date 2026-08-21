import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from main import app
from database import init_db, get_connection, execute_query
from security_utils import create_access_token
from scripts.admin.seed_production_patient import seed_production_patient
from notification_service import send_dual_email

class TestProductionLaunchReadiness(unittest.TestCase):
    """
    Тестовый набор для проверки готовности платформы к боевому запуску (Phase 4 / Production Launch).
    """

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_seed_production_patient_execution(self):
        """1. Тест запуска seed_production_patient с валидным именем папки (идемпотентность и возврат доступов)."""
        folder_name = "Тестовый Пациент"
        res = seed_production_patient(folder_name, custom_password="ProductionTest2026!")
        
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["folder_name"], folder_name)
        self.assertEqual(res["patient_folder_id"], f"disk:/{folder_name}")
        self.assertTrue(len(res["access_token"]) > 20)
        self.assertIn("/app/?token=", res["login_url"])

    def test_02_dual_email_dispatch_logic(self):
        """2. Тест функции дублирования почтовых уведомлений send_dual_email."""
        with patch("notification_service.NotificationService.send_smtp_email", return_value=True) as mock_smtp:
            res = send_dual_email(
                subject="Тест готовности к боевому запуску",
                html_body="<p>Тестовое сообщение</p>",
                primary_email="konsultantms@yandex.com",
                secondary_email="sergo123qwe321@gmail.com"
            )
            self.assertTrue(res["konsultantms@yandex.com"])
            self.assertTrue(res["sergo123qwe321@gmail.com"])
            self.assertTrue(res["success"])
            self.assertEqual(mock_smtp.call_count, 2)

    def test_03_admin_diagnose_folder_endpoint(self):
        """3. Тест защищенного диагностического эндпоинта GET /api/v1/admin/diagnose/folder/{folder_name}."""
        admin_token = create_access_token({"sub": "admin", "role": "ADMIN"})
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = self.client.get("/api/v1/admin/diagnose/folder/Тестовый Пациент", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["exists_in_db"])
        self.assertIn("patient_access_record", data)
        self.assertIn("cache_exists_on_disk", data)
        self.assertIn("last_etl_log", data)

    def test_04_rbac_security_for_production_endpoints(self):
        """4. Финальный аудит RBAC: проверка защиты всех боевых эндпоинтов от неавторизованного доступа."""
        # 4a. Пациентский шеринг без токена -> 401
        res_share_unauth = self.client.post("/api/v1/patient/share", json={"ttl_hours": 24})
        self.assertEqual(res_share_unauth.status_code, 401)

        # 4b. Докторское резюме без токена -> 401
        res_summary_unauth = self.client.get("/api/v1/doctor/patient/disk:/Тестовый Пациент/summary")
        self.assertEqual(res_summary_unauth.status_code, 401)

        # 4c. Докторский PDF без токена -> 401
        res_pdf_unauth = self.client.get("/api/v1/doctor/patient/disk:/Тестовый Пациент/summary/pdf")
        self.assertEqual(res_pdf_unauth.status_code, 401)

        # 4d. Доктор с токеном без гранта -> 403
        doc_token = create_access_token({"sub": "999", "doctor_id": 999, "role": "DOCTOR"})
        headers_doc = {"Authorization": f"Bearer {doc_token}"}
        res_summary_forbidden = self.client.get("/api/v1/doctor/patient/disk:/UnknownPatient/summary", headers=headers_doc)
        self.assertEqual(res_summary_forbidden.status_code, 403)

    def test_05_rate_limiting_on_auth_endpoints(self):
        """5. Тест работы Rate Limiter на эндпоинтах авторизации."""
        test_ip = "198.51.100.77"
        headers = {"X-Forwarded-For": test_ip}

        # 5 неудачных попыток входа администратора
        for _ in range(5):
            self.client.post("/api/v1/admin/login", json={"username": "bad_user", "password": "bad_password"}, headers=headers)

        # 6-я попытка должна вернуть 429 Too Many Requests
        res_blocked = self.client.post("/api/v1/admin/login", json={"username": "bad_user", "password": "bad_password"}, headers=headers)
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Retry-After", res_blocked.headers)

if __name__ == '__main__':
    unittest.main()
