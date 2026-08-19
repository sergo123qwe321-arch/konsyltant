import unittest
import uuid
from fastapi.testclient import TestClient
from main import app
from database import init_db, count_active_shares, revoke_share_grant, get_share_grant_by_id
from security_utils import create_access_token

class TestSharingLimit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        
        cls.patient_folder = f"patient_limit_test_{uuid.uuid4().hex[:6]}"
        cls.other_patient_folder = f"patient_other_{uuid.uuid4().hex[:6]}"
        
        # Токен основного пациента
        cls.patient_token = create_access_token({
            "sub": "patient_limit_user",
            "role": "PATIENT",
            "allowed_folder": cls.patient_folder
        })
        cls.patient_headers = {"Authorization": f"Bearer {cls.patient_token}"}
        
        # Токен другого пациента
        cls.other_token = create_access_token({
            "sub": "patient_other_user",
            "role": "PATIENT",
            "allowed_folder": cls.other_patient_folder
        })
        cls.other_headers = {"Authorization": f"Bearer {cls.other_token}"}

    def test_sharing_limit_and_revocation_lifecycle(self):
        """
        Полный жизненный цикл проверки лимита (2 активные ссылки), блокировки 3-й (429),
        отзыва (DELETE) и повторного создания.
        """
        # 1. Первая ссылка создается успешно
        res1 = self.client.post("/api/v1/patient/share", json={"expires_in_hours": 24}, headers=self.patient_headers)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertIn("share_token", data1)
        self.assertEqual(count_active_shares(self.patient_folder), 1)

        # 2. Вторая ссылка создается успешно
        res2 = self.client.post("/api/v1/patient/share", json={"expires_in_hours": 48}, headers=self.patient_headers)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertIn("share_token", data2)
        self.assertEqual(count_active_shares(self.patient_folder), 2)

        # 3. Список активных ссылок возвращает 2 ссылки
        list_res = self.client.get("/api/v1/patient/shares", headers=self.patient_headers)
        self.assertEqual(list_res.status_code, 200)
        list_data = list_res.json()
        self.assertEqual(list_data["active_count"], 2)
        self.assertEqual(len(list_data["shares"]), 2)
        grant_id_to_revoke = list_data["shares"][0]["id"]

        # 4. Попытка создать 3-ю активную ссылку блокируется (HTTP 429)
        res3 = self.client.post("/api/v1/patient/share", json={"expires_in_hours": 24}, headers=self.patient_headers)
        self.assertEqual(res3.status_code, 429)
        err_data = res3.json()
        self.assertIn("detail", err_data)
        detail = err_data["detail"]
        if isinstance(detail, dict):
            self.assertIn("2 активные ссылки", detail.get("message", ""))
            self.assertEqual(detail.get("active_count"), 2)
            self.assertEqual(detail.get("max_allowed"), 2)
        else:
            self.assertIn("2 активные ссылки", detail)

        # 5. Попытка другого пациента отозвать чужую ссылку блокируется (HTTP 403)
        revoke_other_res = self.client.delete(f"/api/v1/patient/share/{grant_id_to_revoke}", headers=self.other_headers)
        self.assertEqual(revoke_other_res.status_code, 403)
        self.assertIn("чужую", revoke_other_res.json().get("detail", ""))

        # 6. Отзыв несуществующей ссылки возвращает 404
        revoke_404_res = self.client.delete("/api/v1/patient/share/99999999", headers=self.patient_headers)
        self.assertEqual(revoke_404_res.status_code, 404)

        # 7. Владелец успешно отзывает одну из ссылок
        revoke_res = self.client.delete(f"/api/v1/patient/share/{grant_id_to_revoke}", headers=self.patient_headers)
        self.assertEqual(revoke_res.status_code, 200)
        self.assertEqual(revoke_res.json().get("status"), "success")
        self.assertEqual(count_active_shares(self.patient_folder), 1)

        # 8. После отзыва создание новой ссылки снова успешно разрешено (HTTP 200)
        res4 = self.client.post("/api/v1/patient/share", json={"expires_in_hours": 24}, headers=self.patient_headers)
        self.assertEqual(res4.status_code, 200)
        self.assertEqual(count_active_shares(self.patient_folder), 2)

if __name__ == '__main__':
    unittest.main()

