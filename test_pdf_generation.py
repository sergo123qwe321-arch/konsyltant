import unittest
import io
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from database import init_db, create_share_grant, create_doctor
from security_utils import create_access_token
from pdf_generator import generate_summary_pdf

class TestPDFGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        
        # Создаем верифицированного врача в БД
        doc = create_doctor(
            full_name="Др. Педиатров Иван Сергеевич",
            specialty="Ведущий детский нейропсихолог",
            license_number="DOC-PDF-TEST-001",
            is_verified=True
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
        
        # Токен пациента
        cls.patient_token = create_access_token({
            "sub": "patient_pdf_user_1",
            "role": "PATIENT",
            "allowed_folder": "folder_patient_pdf_1"
        })
        cls.patient_headers = {"Authorization": f"Bearer {cls.patient_token}"}

    def test_pdf_unauthorized(self):
        """1. Запрос PDF без JWT токена возвращает HTTP 401 Unauthorized."""
        res = self.client.get("/api/v1/doctor/patient/folder_test_pdf_01/summary/pdf")
        self.assertEqual(res.status_code, 401)
        self.assertIn("Отсутствует токен", res.json().get("detail", ""))

    def test_pdf_forbidden_no_grant(self):
        """2. Врач без активного гранта на доступ к папке получает HTTP 403 Forbidden."""
        unshared_folder = "folder_secret_patient_pdf_99"
        res = self.client.get(
            f"/api/v1/doctor/patient/{unshared_folder}/summary/pdf",
            headers=self.doctor_headers
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("не предоставлен или срок действия истек", res.json().get("detail", ""))

    @patch("rag.fetch_yandex_cache_json")
    @patch("rag.get_gigachat_token")
    @patch("requests.post")
    def test_pdf_success(self, mock_post, mock_get_token, mock_fetch):
        """3. Врач с валидным грантом получает HTTP 200 и бинарный PDF."""
        valid_folder = "folder_pdf_success_01"
        create_share_grant(patient_folder_id=valid_folder, doctor_id=self.doctor_id, ttl_hours=72)
        
        mock_fetch.return_value = ({
            "chunks": [
                "Пациент: Артем, 7 лет. Диагноз: ЗПР, СДВГ. Аллергия: цитрусовые, пенициллин.",
                "Рекомендации: Сенсорная интеграция, ЛФК, наблюдение невролога."
            ]
        }, True)
        mock_get_token.return_value = "mock_token_pdf_123"
        
        mock_llm_json = {
            "choices": [{
                "message": {
                    "content": '{\n  "anamnesis": "Мальчик 7 лет с задержкой развития и невнимательностью.",\n  "diagnoses": ["ЗПР", "СДВГ"],\n  "contraindications": ["Цитрусовые", "Пенициллин"],\n  "drug_interactions": ["Седативные препараты ограничить"],\n  "recommendations": ["Сенсорная интеграция 2 раза в неделю", "ЛФК"]\n}'
                }
            }]
        }
        
        class MockResponse:
            status_code = 200
            def json(self):
                return mock_llm_json
            def raise_for_status(self):
                pass
                
        mock_post.return_value = MockResponse()
        
        res = self.client.get(
            f"/api/v1/doctor/patient/{valid_folder}/summary/pdf",
            headers=self.doctor_headers
        )
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/pdf")
        self.assertTrue(res.content.startswith(b"%PDF"))
        self.assertGreater(len(res.content), 5000)

    @patch("rag.fetch_yandex_cache_json")
    @patch("rag.get_gigachat_token")
    @patch("requests.post")
    def test_pdf_content_type_and_filename(self, mock_post, mock_get_token, mock_fetch):
        """4. Проверка Content-Type и заголовка Content-Disposition с именем файла."""
        valid_folder = "folder_pdf_headers_02"
        create_share_grant(patient_folder_id=valid_folder, doctor_id=self.doctor_id, ttl_hours=72)
        
        mock_fetch.return_value = ({"chunks": ["Текст документа"]}, True)
        mock_get_token.return_value = "mock_token_123"
        
        mock_llm_json = {
            "choices": [{
                "message": {
                    "content": '{"anamnesis": "Тест", "diagnoses": ["D1"], "contraindications": [], "drug_interactions": [], "recommendations": []}'
                }
            }]
        }
        
        class MockResponse:
            status_code = 200
            def json(self):
                return mock_llm_json
            def raise_for_status(self):
                pass
                
        mock_post.return_value = MockResponse()
        
        res = self.client.get(
            f"/api/v1/doctor/patient/{valid_folder}/summary/pdf",
            headers=self.doctor_headers
        )
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/pdf")
        
        cd_header = res.headers.get("content-disposition", "")
        self.assertIn("attachment", cd_header)
        self.assertIn("medical_summary_folder_pdf_headers_02_", cd_header)
        self.assertTrue(cd_header.endswith('.pdf"'))

    def test_pdf_cyrillic_generation_direct(self):
        """5. Прямая генерация PDF с богатым кириллическим текстом и проверка валидности."""
        summary = {
            "anamnesis": "Пациент наблюдается в клинике с диагнозом ранний детский аутизм. Положительная динамика на фоне занятий.",
            "diagnoses": ["РДА (Ранний детский аутизм)", "Сенсорная алалия"],
            "contraindications": ["Острая реакция на яркий свет и громкие звуки", "Аллергия на парацетамол"],
            "drug_interactions": ["Не совмещать с антигистаминными первого поколения"],
            "recommendations": ["Продолжить курс АВА-терапии", "Консультация сурдолога"]
        }
        doctor = {
            "full_name": "Профессор Нейропсихологии",
            "specialty": "Детский клинический психолог",
            "license_number": "MED-CYRILLIC-888"
        }
        
        pdf_bytes = generate_summary_pdf(summary, doctor, "disk:/Тестовый Пациент с Кириллицей")
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 10000)

if __name__ == '__main__':
    unittest.main()

