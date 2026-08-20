import os
import glob
import re
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from database import init_db
from security_utils import create_access_token
from folder_watcher import download_yandex_file_bytes, upload_json_to_yandex_disk
from document_parser import parse_document_bytes, chunk_text
from rag import fetch_yandex_cache_json

class TestYandexDiskAutonomy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({
            "sub": "admin_test_user",
            "role": "ADMIN",
            "full_name": "Администратор Системы"
        })
        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}

    def test_01_no_google_imports(self):
        """1. Статический анализ: во всех .py файлах отсутствуют импорты google/googleapiclient/drive_api."""
        py_files = glob.glob("*.py") + glob.glob("scripts/**/*.py", recursive=True)
        self.assertTrue(len(py_files) > 0, "Python файлы проекта не найдены")

        forbidden_patterns = [
            re.compile(r'^\s*import\s+google', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\s*from\s+google', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\s*import\s+googleapiclient', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\s*from\s+googleapiclient', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\s*import\s+drive_api', re.IGNORECASE | re.MULTILINE),
            re.compile(r'^\s*from\s+drive_api', re.IGNORECASE | re.MULTILINE),
        ]

        violations = []
        for file_path in py_files:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for pattern in forbidden_patterns:
                    matches = pattern.findall(content)
                    if matches:
                        violations.append(f"{file_path}: {matches}")

        self.assertEqual(len(violations), 0, f"Обнаружены запрещенные Google-импорты: {violations}")

    def test_02_no_google_credentials_files(self):
        """2. В репозитории полностью отсутствует файл credentials.json."""
        self.assertFalse(os.path.exists("credentials.json"), "Файл credentials.json найден в корне проекта!")
        for root, dirs, files in os.walk("."):
            if ".git" in root:
                continue
            self.assertNotIn("credentials.json", files, f"Файл credentials.json найден в {root}")

    def test_03_no_google_in_requirements(self):
        """3. В requirements.txt отсутствуют библиотеки google-api-python-client и google-auth."""
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read().lower()

        forbidden_libs = [
            "google-api-python-client",
            "google-auth",
            "google-auth-httplib2",
            "google-auth-oauthlib"
        ]
        for lib in forbidden_libs:
            self.assertNotIn(lib, content, f"Библиотека {lib} обнаружена в requirements.txt")

    def test_04_folder_watcher_uses_only_yandex(self):
        """4. folder_watcher.py использует только Yandex Disk API и не содержит Google Drive логики."""
        with open("folder_watcher.py", "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("cloud-api.yandex.net", code)
        self.assertNotIn("googleapis.com", code)
        self.assertNotIn("get_drive_service", code)

    def test_05_rag_reads_only_yandex_cache(self):
        """5. rag.py читает JSON-кэш только через Yandex Disk API."""
        with open("rag.py", "r", encoding="utf-8") as f:
            code = f.read()

        self.assertIn("fetch_yandex_cache_json", code)
        self.assertIn("cloud-api.yandex.net", code)
        self.assertNotIn("googleapis.com", code)
        self.assertNotIn("get_drive_service", code)

    def test_06_etl_pipeline_works_with_yandex_mock(self):
        """6. End-to-end тест ETL: скачивание -> парсинг -> чанкование -> сборка кэша."""
        # Мокаем ответ Яндекс.Диска
        fake_text_bytes = "Диагноз: ЗРР 2 степени. Назначены занятия с логопедом.".encode("utf-8")
        
        with patch("requests.get") as mock_get:
            mock_res = MagicMock()
            mock_res.status_code = 200
            mock_res.content = fake_text_bytes
            mock_res.json.return_value = {"file": "https://downloader.yandex.net/fake_url"}
            mock_get.return_value = mock_res

            content = download_yandex_file_bytes("disk:/Тестовый_Пациент/заключение.txt")
            self.assertEqual(content, fake_text_bytes)

            parsed_text = parse_document_bytes(content, "заключение.txt")
            self.assertIn("ЗРР", parsed_text)

            chunks = chunk_text(parsed_text, chunk_size=500, overlap=50)
            self.assertTrue(len(chunks) > 0)
            self.assertIn("ЗРР", chunks[0])

    def test_07_yandex_health_endpoint_auth_and_response(self):
        """7. Эндпоинт GET /api/v1/health/yandex-disk защищен правами ADMIN и возвращает статус."""
        # Без авторизации -> 401
        res_unauth = self.client.get("/api/v1/health/yandex-disk")
        self.assertEqual(res_unauth.status_code, 401)

        # С авторизацией администратора и замоканным ответом Яндекс.Диска -> 200 / status OK
        with patch("requests.get") as mock_get:
            mock_res = MagicMock()
            mock_res.status_code = 200
            mock_res.json.return_value = {
                "total_space": 10737418240,
                "used_space": 104857600,
                "trash_size": 0
            }
            mock_get.return_value = mock_res

            res_admin = self.client.get("/api/v1/health/yandex-disk", headers=self.admin_headers)
            self.assertEqual(res_admin.status_code, 200)
            data = res_admin.json()
            self.assertEqual(data.get("status"), "OK")
            self.assertIn("yandex_disk", data)
            self.assertEqual(data["yandex_disk"]["status"], "available")
            self.assertEqual(data["yandex_disk"]["total_space_bytes"], 10737418240)

if __name__ == '__main__':
    unittest.main()

