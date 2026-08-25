import unittest
import os
import io
from fastapi.testclient import TestClient
import database
from main import app
from security_utils import create_access_token

class TestLocalUploads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({
            "sub": "admin",
            "role": "ADMIN",
            "full_name": "Администратор Клиники"
        })

    def test_admin_upload_saves_locally(self):
        """Тест загрузки файла администратором с сохранением в static/uploads/"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        file_content = b"Sample cover image binary data"
        files = {"file": ("test_cover.jpg", io.BytesIO(file_content), "image/jpeg")}
        
        res = self.client.post("/api/v1/admin/upload", files=files, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["url"].startswith("/static/uploads/"))
        self.assertTrue(data["local_url"].startswith("/static/uploads/"))
        self.assertNotIn("yandex_url", data)
        
        filename = data["filename"]
        local_path = os.path.join("static", "uploads", filename)
        self.assertTrue(os.path.exists(local_path))
        with open(local_path, "rb") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, file_content)

    def test_admin_upload_unauthorized(self):
        """Неавторизованный пользователь не может загружать файлы"""
        files = {"file": ("test_cover.jpg", io.BytesIO(b"test"), "image/jpeg")}
        res = self.client.post("/api/v1/admin/upload", files=files)
        self.assertEqual(res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
