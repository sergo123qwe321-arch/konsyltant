import os
import io
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
from fastapi.testclient import TestClient
from main import app
from database import init_db, create_patient_access
from security_utils import create_access_token
from folder_watcher import should_process_folder, record_etl_log, get_last_etl_logs
from document_parser import parse_document_bytes
from notification_service import NotificationService

class TestETLDiagnostic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({
            "sub": "admin_diagnose_user",
            "role": "ADMIN",
            "full_name": "Администратор Клиники"
        })
        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}

    def test_01_excluded_folders_skipped(self):
        """1. Проверка исключения служебных папок (Загрузки, Trash, Корзина) из сканирования."""
        self.assertFalse(should_process_folder("Загрузки"))
        self.assertFalse(should_process_folder("загрузки"))
        self.assertFalse(should_process_folder("disk:/Загрузки"))
        self.assertFalse(should_process_folder("disk:/Trash"))
        self.assertFalse(should_process_folder("Корзина"))
        self.assertFalse(should_process_folder("disk:/Archive/old"))

        # Разрешенные папки пациентов
        self.assertTrue(should_process_folder("Иванов Иван"))
        self.assertTrue(should_process_folder("disk:/Дюзгёрен Арон Альп"))
        self.assertTrue(should_process_folder("disk:/Тестовый Пациент"))

    def test_02_image_processing_ocr(self):
        """2. Проверка корректной обработки изображений (JPG, PNG, TIFF) через document_parser."""
        # Создаем простое RGB изображение в памяти
        img = Image.new("RGB", (200, 60), color=(255, 255, 255))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        jpg_bytes = img_byte_arr.getvalue()

        # Мокаем вызов pytesseract для воспроизводимости как локально, так и в CI/Docker
        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.return_value = "Диагноз: Норма. Назначены упражнения."
        with patch("document_parser.pytesseract", mock_pytesseract):
            text_jpg = parse_document_bytes(jpg_bytes, "Скан_1.jpg", "image/jpeg")
            self.assertIn("Диагноз: Норма", text_jpg)

            png_byte_arr = io.BytesIO()
            img.save(png_byte_arr, format='PNG')
            text_png = parse_document_bytes(png_byte_arr.getvalue(), "Скан_2.png", "image/png")
            self.assertIn("Диагноз: Норма", text_png)

    def test_03_diagnostic_endpoint(self):
        """3. Проверка диагностического эндпоинта GET /api/v1/admin/diagnose/folder/{folder_name}."""
        # Создаем тестовую запись в БД
        test_folder = "disk:/Диагностика Пациент"
        access_token = create_patient_access("DiagPass2026!", test_folder)
        record_etl_log("Диагностика Пациент", "ETL успешно завершен: 10 чанков создано")

        # 3.1. Запрос без авторизации -> 401
        res_unauth = self.client.get(f"/api/v1/admin/diagnose/folder/Диагностика Пациент")
        self.assertEqual(res_unauth.status_code, 401)

        # 3.2. Запрос с токеном администратора и моком Яндекс.Диска -> 200
        with patch("requests.get") as mock_get:
            # Мок проверки ресурса
            mock_res_meta = MagicMock()
            mock_res_meta.status_code = 200
            mock_res_meta.json.return_value = {
                "name": "_Диагностика_Пациент_cache.json",
                "size": 4096,
                "href": "https://downloader.yandex.net/fake_cache_url"
            }

            mock_res_data = MagicMock()
            mock_res_data.status_code = 200
            mock_res_data.json.return_value = {
                "patient_folder": "Диагностика Пациент",
                "chunks": ["--- Файл: Заключение.pdf ---\nАнамнез: ЗРР 2 степени.", "Рекомендации: Логопед."]
            }

            mock_get.side_effect = [mock_res_meta, mock_res_meta, mock_res_data]

            res = self.client.get(f"/api/v1/admin/diagnose/folder/Диагностика Пациент", headers=self.admin_headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()

            self.assertEqual(data["folder_name"], "Диагностика Пациент")
            self.assertTrue(data["exists_in_db"])
            self.assertIsNotNone(data["patient_access_record"])
            self.assertEqual(data["patient_access_record"]["access_token"], access_token)
            self.assertEqual(data["patient_access_record"]["role"], "PATIENT")
            self.assertTrue(data["cache_exists_on_disk"])
            self.assertEqual(data["cache_chunk_count"], 2)
            self.assertIn("ЗРР", data["cache_sample"])
            self.assertIn("ETL успешно завершен", data["last_etl_log"])

    def test_04_patient_access_links_and_routing(self):
        """4. Проверка корректного формирования ссылок доступа и SPA-роутинга."""
        # 4.1. Ссылка в письме формируется строго в формате /app/?token=... (без :8000 и без /app/TOKEN)
        with patch("notification_service.NotificationService.send_smtp_email") as mock_smtp:
            mock_smtp.return_value = True
            NotificationService.send_welcome_email(
                recipient_email="test@example.com",
                access_token="valid_token_xyz_123",
                passcode="SecurePass123!",
                folder_name="Иванов Иван",
                base_url="http://159.194.232.74:8000"  # Намеренно передаем некорректный legacy base_url
            )
            # Проверяем, что в HTML тело письма попала очищенная ссылка https://xn--g1aj3a.site/app/?token=...
            called_body = mock_smtp.call_args[0][1]
            self.assertIn("/app/?token=valid_token_xyz_123", called_body)
            self.assertNotIn(":8000", called_body)

        # 4.2. Редиректы в FastAPI:
        # Редирект /?token=... -> /app/?token=...
        res_root = self.client.get("/?token=test_tok_99", follow_redirects=False)
        self.assertEqual(res_root.status_code, 307)
        self.assertEqual(res_root.headers.get("location"), "/app/?token=test_tok_99")

        # Редирект /app/test_tok_99 -> /app/?token=test_tok_99
        res_app_path = self.client.get("/app/test_tok_99", follow_redirects=False)
        self.assertEqual(res_app_path.status_code, 307)
        self.assertEqual(res_app_path.headers.get("location"), "/app/?token=test_tok_99")

if __name__ == '__main__':
    unittest.main()

