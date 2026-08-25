import unittest
import os
import io
import bcrypt
from fastapi.testclient import TestClient
import database
from main import app
from security_utils import create_access_token

class TestDoctorNotesAndDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        database.ensure_indexes()
        cls.client = TestClient(app)
        
        # Создаем тестового врача
        conn = database.get_connection()
        cursor = conn.cursor()
        database.execute_query(cursor, "DELETE FROM doctors WHERE license_number = ?", ("LIC-TEST-DASHBOARD",))
        conn.commit()
        conn.close()
        
        pwd_hash = bcrypt.hashpw("DocPass123!".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cls.doctor = database.create_doctor(
            full_name="Доктор Тестовый",
            specialty="Детский невролог",
            license_number="LIC-TEST-DASHBOARD",
            is_verified=True,
            email="doc_dashboard@cmz.site",
            password_hash=pwd_hash
        )
        cls.doctor_token = create_access_token({
            "sub": str(cls.doctor["id"]),
            "doctor_id": cls.doctor["id"],
            "role": "DOCTOR",
            "full_name": cls.doctor["full_name"],
            "specialty": cls.doctor["specialty"]
        })
        
        # Создаем тестовый шеринг-грант
        cls.patient_folder = "disk:/Тестовый Пациент Dashboard"
        cls.share_token = database.create_share_grant(
            patient_folder_id=cls.patient_folder,
            doctor_id=cls.doctor["id"],
            ttl_hours=72
        )

    def test_01_doctor_view_document_endpoint(self):
        """Тест эндпоинта просмотра диагностического документа врачом"""
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        res = self.client.get(
            f"/api/v1/doctor/patient-records/{self.share_token}/document/диагностика.pdf",
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Content-Disposition", res.headers)
        self.assertIn("inline", res.headers["Content-Disposition"])
        self.assertTrue(len(res.content) > 0)

    def test_02_doctor_view_document_unauthorized(self):
        """Без токена врача доступ к документу запрещен"""
        res = self.client.get(
            f"/api/v1/doctor/patient-records/{self.share_token}/document/диагностика.pdf"
        )
        self.assertEqual(res.status_code, 401)

    def test_03_doctor_notes_crud(self):
        """Тест полного жизненного цикла заметок врача по пациенту"""
        headers = {"Authorization": f"Bearer {self.doctor_token}"}
        
        # 1. Получение заметки (пусто)
        res = self.client.get(f"/api/v1/doctor/patient/{self.patient_folder}/notes", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        # 2. Сохранение заметки
        note_text = "Клиническая динамика положительная. Рекомендован курс нейрогимнастики 2 раза в неделю."
        res = self.client.post(
            f"/api/v1/doctor/patient/{self.patient_folder}/notes",
            json={"note_text": note_text},
            headers=headers
        )
        self.assertEqual(res.status_code, 200)
        saved_note = res.json()["note"]
        self.assertEqual(saved_note["note_text"], note_text)
        note_id = saved_note["id"]
        
        # 3. Повторное чтение
        res = self.client.get(f"/api/v1/doctor/patient/{self.patient_folder}/notes", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["note"]["note_text"], note_text)
        
        # 4. Удаление заметки
        res = self.client.delete(f"/api/v1/doctor/notes/{note_id}", headers=headers)
        self.assertEqual(res.status_code, 200)
        
        # 5. Проверка после удаления
        res = self.client.get(f"/api/v1/doctor/patient/{self.patient_folder}/notes", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.json()["note"])

    def test_04_doctor_notes_unauthorized(self):
        """Без роли врача доступ к заметкам запрещен"""
        res = self.client.get(f"/api/v1/doctor/patient/{self.patient_folder}/notes")
        self.assertEqual(res.status_code, 401)

if __name__ == "__main__":
    unittest.main()
