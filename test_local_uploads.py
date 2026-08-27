import unittest
import os
import io
from fastapi.testclient import TestClient
import database
from main import app, UPLOAD_DIR
from security_utils import create_access_token

class TestLocalUploads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.ensure_indexes()
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({'sub': 'admin', 'role': 'ADMIN', 'full_name': 'Администратор'})
        cls.doctor_token = create_access_token({'sub': '1', 'doctor_id': 1, 'role': 'DOCTOR', 'full_name': 'Врач'})
        cls.patient_token = create_access_token({'sub': 'patient_1', 'role': 'PATIENT', 'full_name': 'Пациент', 'allowed_folder': 'disk:/Пациент'})
        cls.created_files = []

    @classmethod
    def tearDownClass(cls):
        for f in cls.created_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

    def test_01_upload_image_success(self):
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        fake_image = io.BytesIO(b'\xFF\xD8\xFF\xE0\x00\x10JFIF' + b'testimagedata' * 10)
        files = {'file': ('test_cover.jpg', fake_image, 'image/jpeg')}
        res = self.client.post('/api/v1/admin/upload', headers=headers, files=files)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(data['url'].startswith('/static/uploads/'))
        self.assertTrue(data['filename'].endswith('.jpg'))
        self.assertTrue(data['size_bytes'] > 0)
        file_path = os.path.join(UPLOAD_DIR, data['filename'])
        self.assertTrue(os.path.exists(file_path))
        self.created_files.append(file_path)

    def test_02_upload_video_success(self):
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        fake_video = io.BytesIO(b'\x00\x00\x00\x18ftypmp42' + b'testvideodata' * 20)
        files = {'file': ('demo_lesson.mp4', fake_video, 'video/mp4')}
        res = self.client.post('/api/v1/admin/upload', headers=headers, files=files)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(data['url'].startswith('/static/uploads/'))
        self.assertTrue(data['filename'].endswith('.mp4'))
        file_path = os.path.join(UPLOAD_DIR, data['filename'])
        self.assertTrue(os.path.exists(file_path))
        self.created_files.append(file_path)

    def test_03_upload_unauthorized(self):
        fake_image = io.BytesIO(b'imagebytes')
        files = {'file': ('test.jpg', fake_image, 'image/jpeg')}
        res = self.client.post('/api/v1/admin/upload', files=files)
        self.assertEqual(res.status_code, 401)

    def test_04_upload_forbidden_role(self):
        fake_image = io.BytesIO(b'imagebytes')
        files = {'file': ('test.jpg', fake_image, 'image/jpeg')}
        res_doc = self.client.post('/api/v1/admin/upload', headers={'Authorization': f'Bearer {self.doctor_token}'}, files=files)
        self.assertEqual(res_doc.status_code, 403)
        fake_image.seek(0)
        files = {'file': ('test.jpg', fake_image, 'image/jpeg')}
        res_pat = self.client.post('/api/v1/admin/upload', headers={'Authorization': f'Bearer {self.patient_token}'}, files=files)
        self.assertEqual(res_pat.status_code, 403)

    def test_05_upload_invalid_extension(self):
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        fake_file = io.BytesIO(b'executable')
        files = {'file': ('danger.exe', fake_file, 'application/octet-stream')}
        res = self.client.post('/api/v1/admin/upload', headers=headers, files=files)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Неподдерживаемый формат', res.json()['detail'])

    def test_06_upload_empty_file(self):
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        empty_file = io.BytesIO(b'')
        files = {'file': ('empty.png', empty_file, 'image/png')}
        res = self.client.post('/api/v1/admin/upload', headers=headers, files=files)
        self.assertEqual(res.status_code, 400)
        self.assertIn('файл пуст', res.json()['detail'])

if __name__ == '__main__':
    unittest.main()
