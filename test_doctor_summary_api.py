import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from database import init_db, create_share_grant, create_doctor, get_connection, execute_query
from security_utils import create_access_token

class TestDoctorSummaryAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        
        # Создаем верифицированного врача в базе данных для валидации внешнего ключа в PostgreSQL
        doc = create_doctor(
            full_name="Др. Айболит Тестовый",
            specialty="Педиатр-Нейропсихолог",
            license_number="TEST-DOC-SUMMARY-99"
        )
        cls.doctor_id = doc["id"]
        cls.doctor_token = create_access_token({
            "sub": str(cls.doctor_id),
            "doctor_id": cls.doctor_id,
            "role": "DOCTOR",
            "full_name": doc["full_name"],
            "specialty": doc["specialty"]
        })
        cls.doctor_headers = {"Authorization": f"Bearer {cls.doctor_token}"}
        
        # Создаем токен пациента (не врача)
        cls.patient_token = create_access_token({
            "sub": "patient_token_123",
            "role": "PATIENT",
            "allowed_folder": "folder_patient_123"
        })
        cls.patient_headers = {"Authorization": f"Bearer {cls.patient_token}"}

    def test_unauthorized_access(self):
        """1. Запрос без JWT токена возвращает HTTP 401 Unauthorized."""
        res = self.client.post("/api/v1/doctor/patient/folder_test_patient_01/summary")
        self.assertEqual(res.status_code, 401)
        self.assertIn("Отсутствует токен", res.json().get("detail", ""))

    def test_forbidden_patient_role(self):
        """1b. Запрос с токеном пациента (роль != DOCTOR) возвращает HTTP 403 Forbidden."""
        res = self.client.post(
            "/api/v1/doctor/patient/folder_test_patient_01/summary",
            headers=self.patient_headers
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("требуются права врача", res.json().get("detail", ""))

    def test_forbidden_no_grant(self):
        """2. Врач без активного гранта на доступ к папке получает HTTP 403 Forbidden."""
        unshared_folder = "folder_secret_patient_999"
        res = self.client.post(
            f"/api/v1/doctor/patient/{unshared_folder}/summary",
            headers=self.doctor_headers
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("не предоставлен или срок действия истек", res.json().get("detail", ""))

    def test_forbidden_expired_grant(self):
        """3. Врач с истекшим грантом получает HTTP 403 Forbidden."""
        expired_folder = "folder_expired_patient_888"
        # Создаем грант с отрицательным TTL (-24 часа)
        create_share_grant(patient_folder_id=expired_folder, doctor_id=self.doctor_id, ttl_hours=-24)
        
        res = self.client.post(
            f"/api/v1/doctor/patient/{expired_folder}/summary",
            headers=self.doctor_headers
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("не предоставлен или срок действия истек", res.json().get("detail", ""))

    @patch("rag.fetch_yandex_cache_json")
    def test_missing_cache_file(self, mock_fetch):
        """4. Запрос для папки без _cache.json возвращает HTTP 404 Not Found."""
        valid_folder = "folder_no_cache_patient_777"
        # Создаем активный грант
        create_share_grant(patient_folder_id=valid_folder, doctor_id=self.doctor_id, ttl_hours=48)
        
        # Мокаем отсутствие кэша
        mock_fetch.return_value = (None, False)
        
        res = self.client.post(
            f"/api/v1/doctor/patient/{valid_folder}/summary",
            headers=self.doctor_headers
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn("еще обрабатываются", res.json().get("detail", ""))

    @patch("rag.fetch_yandex_cache_json")
    @patch("rag.get_gigachat_token")
    @patch("requests.post")
    def test_success_summary_generation(self, mock_post, mock_get_token, mock_fetch):
        """5. Врач с валидным грантом получает HTTP 200 и структурированное JSON-резюме."""
        valid_folder = "folder_valid_patient_001"
        create_share_grant(patient_folder_id=valid_folder, doctor_id=self.doctor_id, ttl_hours=72)
        
        # Мокаем кэш документов
        mock_fetch.return_value = ({
            "chunks": [
                "Пациент: Иван, 6 лет. Жалобы: задержка речевого развития, моторная неловкость.",
                "Диагноз: СДВГ, ЗРР. Противопоказания: аллергия на пенициллин, ноотропы с осторожностью."
            ]
        }, True)
        
        # Мокаем GigaChat токен и ответ
        mock_get_token.return_value = "mock_gigachat_token_xyz"
        
        mock_llm_response = {
            "choices": [{
                "message": {
                    "content": '{\n  "anamnesis": "Мальчик 6 лет с задержкой речи и симптомами СДВГ.",\n  "diagnoses": ["СДВГ", "ЗРР"],\n  "contraindications": ["Аллергия на пенициллин"],\n  "drug_interactions": ["Ноотропы требуют контроля"],\n  "recommendations": ["Нейрокоррекция 2 раза в неделю, занятия с логопедом"]\n}'
                }
            }]
        }
        
        class MockResponse:
            status_code = 200
            def json(self):
                return mock_llm_response
            def raise_for_status(self):
                pass
                
        mock_post.return_value = MockResponse()
        
        res = self.client.post(
            f"/api/v1/doctor/patient/{valid_folder}/summary",
            headers=self.doctor_headers
        )
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["patient_folder_id"], valid_folder)
        
        summary = data["summary"]
        self.assertIn("Мальчик 6 лет", summary["anamnesis"])
        self.assertIn("СДВГ", summary["diagnoses"])
        self.assertIn("Аллергия на пенициллин", summary["contraindications"])
        self.assertEqual(len(summary["recommendations"]), 1)

if __name__ == '__main__':
    unittest.main()

