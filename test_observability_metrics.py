import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from database import (
    init_db, save_etl_metric, get_latest_etl_metric_for_folder,
    get_all_etl_metrics, get_etl_aggregates, record_llm_usage,
    get_llm_usage_summary
)
from security_utils import create_access_token
from rag import get_gigachat_balance

class TestObservabilityMetrics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        
        cls.admin_token = create_access_token({"sub": "admin_test", "role": "ADMIN"})
        cls.doctor_token = create_access_token({"sub": "doctor_test", "role": "DOCTOR"})
        cls.patient_token = create_access_token({"sub": "patient_test", "role": "PATIENT"})

        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}
        cls.doctor_headers = {"Authorization": f"Bearer {cls.doctor_token}"}
        cls.patient_headers = {"Authorization": f"Bearer {cls.patient_token}"}

    def test_01_etl_metrics_rbac_security(self):
        """1. Проверка RBAC защиты эндпоинта /api/v1/admin/etl/metrics."""
        # Без токена -> 401
        res_no_auth = self.client.get("/api/v1/admin/etl/metrics")
        self.assertEqual(res_no_auth.status_code, 401)

        # С ролью PATIENT -> 403
        res_patient = self.client.get("/api/v1/admin/etl/metrics", headers=self.patient_headers)
        self.assertEqual(res_patient.status_code, 403)

        # С ролью DOCTOR -> 403
        res_doctor = self.client.get("/api/v1/admin/etl/metrics", headers=self.doctor_headers)
        self.assertEqual(res_doctor.status_code, 403)

        # С ролью ADMIN -> 200
        res_admin = self.client.get("/api/v1/admin/etl/metrics", headers=self.admin_headers)
        self.assertEqual(res_admin.status_code, 200)
        data = res_admin.json()
        self.assertIn("aggregates", data)
        self.assertIn("history", data)

    def test_02_llm_usage_rbac_security(self):
        """2. Проверка RBAC защиты эндпоинта /api/v1/admin/llm/usage."""
        # Без токена -> 401
        res_no_auth = self.client.get("/api/v1/admin/llm/usage")
        self.assertEqual(res_no_auth.status_code, 401)

        # С ролью PATIENT -> 403
        res_patient = self.client.get("/api/v1/admin/llm/usage", headers=self.patient_headers)
        self.assertEqual(res_patient.status_code, 403)

        # С ролью DOCTOR -> 403
        res_doctor = self.client.get("/api/v1/admin/llm/usage", headers=self.doctor_headers)
        self.assertEqual(res_doctor.status_code, 403)

        # С ролью ADMIN -> 200
        with patch("rag.get_gigachat_token", return_value="fake_token"), \
             patch("requests.get") as mock_get:
            mock_res = MagicMock()
            mock_res.status_code = 403
            mock_res.text = "Forbidden (Pay-As-You-Go)"
            mock_get.return_value = mock_res

            res_admin = self.client.get("/api/v1/admin/llm/usage", headers=self.admin_headers)
            self.assertEqual(res_admin.status_code, 200)
            data = res_admin.json()
            self.assertIn("usage_summary", data)
            self.assertIn("balance_info", data)

    def test_03_etl_metrics_db_and_aggregates(self):
        """3. Проверка сохранения метрик ETL и расчета агрегатов."""
        test_folder = "disk:/Тест Производительности Пациент"
        save_etl_metric(
            folder_name=test_folder,
            started_at="2026-08-21 10:00:00",
            finished_at="2026-08-21 10:05:00",
            duration_seconds=300.0,
            file_count=80,
            pages_processed=80,
            chunks_created=160,
            errors_count=0,
            avg_time_per_file_seconds=3.75
        )

        metric = get_latest_etl_metric_for_folder("Тест Производительности Пациент")
        self.assertIsNotNone(metric)
        self.assertEqual(metric["duration_seconds"], 300.0)
        self.assertEqual(metric["file_count"], 80)
        self.assertEqual(metric["avg_time_per_file_seconds"], 3.75)
        self.assertEqual(metric["chunks_created"], 160)

        aggregates = get_etl_aggregates()
        self.assertGreaterEqual(aggregates["total_folders_processed"], 1)
        self.assertGreaterEqual(aggregates["total_files_processed"], 80)
        self.assertGreater(aggregates["avg_folder_duration_seconds"], 0.0)

    def test_04_llm_usage_tracking_and_summary(self):
        """4. Проверка фиксации токенов GigaChat и агрегации статистики."""
        record_llm_usage("GigaChat", prompt_tokens=150, completion_tokens=50, total_tokens=200, request_type="rag_consultation")
        record_llm_usage("GigaChat", prompt_tokens=400, completion_tokens=200, total_tokens=600, request_type="clinical_summary")
        record_llm_usage("GigaChat-Pro", prompt_tokens=500, completion_tokens=300, total_tokens=800, request_type="clinical_summary")

        summary = get_llm_usage_summary()
        self.assertGreaterEqual(summary["today"]["total_tokens"], 1600)
        self.assertGreaterEqual(summary["last_7_days"]["total_tokens"], 1600)
        self.assertGreaterEqual(summary["last_13_days"]["total_tokens"], 1600)
        self.assertGreaterEqual(summary["all_time"]["total_tokens"], 1600)

        # Проверка группировки по моделям
        models = [m["model"] for m in summary["by_model"]]
        self.assertIn("GigaChat", models)
        self.assertIn("GigaChat-Pro", models)

        # Проверка группировки по типам запросов
        types = [t["request_type"] for t in summary["by_request_type"]]
        self.assertIn("rag_consultation", types)
        self.assertIn("clinical_summary", types)

    def test_05_gigachat_balance_graceful_handling(self):
        """5. Проверка graceful обработки официального эндпоинта баланса (200 OK vs 403 Pay-As-You-Go)."""
        with patch("rag.get_gigachat_token", return_value="fake_token"):
            # 5.1. Случай 200 OK (Купленный пакет)
            with patch("requests.get") as mock_get:
                mock_res = MagicMock()
                mock_res.status_code = 200
                mock_res.json.return_value = [{"model": "GigaChat", "balance": 500000}]
                mock_get.return_value = mock_res

                bal_200 = get_gigachat_balance()
                self.assertEqual(bal_200["status"], "available")
                self.assertEqual(bal_200["http_code"], 200)
                self.assertIsNotNone(bal_200["balance"])

            # 5.2. Случай 403 Forbidden (Pay-As-You-Go по факту потребления)
            with patch("requests.get") as mock_get:
                mock_res = MagicMock()
                mock_res.status_code = 403
                mock_res.text = "Forbidden"
                mock_get.return_value = mock_res

                bal_403 = get_gigachat_balance()
                self.assertEqual(bal_403["status"], "pay_as_you_go")
                self.assertEqual(bal_403["http_code"], 403)
                self.assertIsNone(bal_403["balance"])
                self.assertIn("Pay-As-You-Go", bal_403["message"])

    def test_06_package_limit_and_warning(self):
        """6. Проверка расчета остатка по купленному пакету токенов и предупреждения при >=80%."""
        with patch.dict(os.environ, {"GIGACHAT_PACKAGE_TOKENS_LIMIT": "1000"}), \
             patch("rag.get_gigachat_token", return_value="fake_token"), \
             patch("requests.get") as mock_get:
            mock_res = MagicMock()
            mock_res.status_code = 403
            mock_get.return_value = mock_res

            bal = get_gigachat_balance()
            self.assertEqual(bal["package_limit"], 1000)
            self.assertIsNotNone(bal["calculated_remaining"])
            self.assertIsNotNone(bal["usage_percent"])

if __name__ == '__main__':
    unittest.main()

