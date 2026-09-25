import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app, ACTIVE_PATIENT_SYNCS, SYNC_LOCK, run_background_patient_sync
from database import init_db
from security_utils import create_access_token

class TestAsyncSyncAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

        # 1. Токен администратора
        cls.admin_token = create_access_token({
            "sub": "admin_user",
            "role": "ADMIN",
            "full_name": "Администратор Системы"
        })
        cls.admin_headers = {"Authorization": f"Bearer {cls.admin_token}"}

        # 2. Токен пациента 1 («Иванов Иван»)
        cls.patient1_token = create_access_token({
            "sub": "patient_1",
            "role": "PATIENT",
            "allowed_folder": "disk:/Иванов Иван"
        })
        cls.patient1_headers = {"Authorization": f"Bearer {cls.patient1_token}"}

        # 3. Токен пациента 2 («Петров Петр»)
        cls.patient2_token = create_access_token({
            "sub": "patient_2",
            "role": "PATIENT",
            "allowed_folder": "disk:/Петров Петр"
        })
        cls.patient2_headers = {"Authorization": f"Bearer {cls.patient2_token}"}

        # 4. Токен врача
        cls.doctor_token = create_access_token({
            "sub": "doctor_1",
            "role": "DOCTOR",
            "full_name": "Др. Айболит"
        })
        cls.doctor_headers = {"Authorization": f"Bearer {cls.doctor_token}"}

    def setUp(self):
        # Очищаем блокировки перед каждым тестом
        with SYNC_LOCK:
            ACTIVE_PATIENT_SYNCS.clear()

    def tearDown(self):
        # Очищаем блокировки после каждого теста
        with SYNC_LOCK:
            ACTIVE_PATIENT_SYNCS.clear()

    def test_unauthorized_access(self):
        """1. Запрос без JWT токена возвращает HTTP 401 Unauthorized."""
        res = self.client.post("/api/v1/sync/patient", json={"patient_folder": "Любой Пациент"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("Отсутствует токен авторизации", res.json().get("detail", ""))

    def test_empty_folder_validation(self):
        """2. Запрос с пустым именем папки возвращает HTTP 400 Bad Request."""
        res = self.client.post(
            "/api/v1/sync/patient",
            json={"patient_folder": "   "},
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("не может быть пустым", res.json().get("detail", ""))

    def test_patient_cannot_sync_other_folder(self):
        """3. Пациент не может запустить синхронизацию чужой папки (HTTP 403, 152-ФЗ)."""
        res = self.client.post(
            "/api/v1/sync/patient",
            json={"patient_folder": "Петров Петр"},
            headers=self.patient1_headers
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Доступ запрещен", res.json().get("detail", ""))

    def test_patient_can_sync_own_folder(self):
        """4. Пациент может инициировать фоновую синхронизацию собственной папки."""
        with patch("main.sync_patient_folder", return_value=0):
            res = self.client.post(
                "/api/v1/sync/patient",
                json={"patient_folder": "Иванов Иван", "batch_limit": 25},
                headers=self.patient1_headers
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data.get("status"), "started")
            self.assertEqual(data.get("patient_folder"), "Иванов Иван")
            self.assertEqual(data.get("batch_limit"), 25)

    def test_admin_can_sync_any_folder(self):
        """5. Администратор имеет право запускать синхронизацию для любой папки."""
        with patch("main.sync_patient_folder", return_value=0):
            res = self.client.post(
                "/api/v1/sync/patient",
                json={"patient_folder": "Малышкин Даня", "batch_limit": 50},
                headers=self.admin_headers
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data.get("status"), "started")
            self.assertEqual(data.get("patient_folder"), "Малышкин Даня")

    def test_race_condition_conflict_409(self):
        """6. Предотвращение гонки: повторный запуск для активной синхронизации возвращает HTTP 409 already_in_progress."""
        folder = "Малышкин Даня"
        with SYNC_LOCK:
            ACTIVE_PATIENT_SYNCS[folder] = {
                "status": "in_progress",
                "started_at": "2026-09-25T10:00:00",
                "patient_folder": folder
            }

        res = self.client.post(
            "/api/v1/sync/patient",
            json={"patient_folder": folder},
            headers=self.admin_headers
        )
        self.assertEqual(res.status_code, 409)
        data = res.json()
        self.assertEqual(data.get("status"), "already_in_progress")
        self.assertIn("уже выполняется", data.get("detail", ""))

    def test_background_worker_lifecycle(self):
        """7. Воркер run_background_patient_sync корректно выполняет итерации и гарантированно снимает лок."""
        patient = "Тестовый Пациент"
        with SYNC_LOCK:
            ACTIVE_PATIENT_SYNCS[patient] = {
                "status": "in_progress",
                "patient_folder": patient
            }

        # Имитируем два шага: сначала осталось 20 файлов, затем 0 файлов
        mock_sync = MagicMock(side_effect=[20, 0])
        with patch("main.sync_patient_folder", mock_sync):
            run_background_patient_sync(patient, batch_limit=25, pause_seconds=0.01)

        self.assertEqual(mock_sync.call_count, 2)
        # Проверяем, что блокировка была снята в блоке finally
        with SYNC_LOCK:
            self.assertNotIn(patient, ACTIVE_PATIENT_SYNCS)

    def test_background_worker_exception_cleanup(self):
        """8. При исключении в воркере блокировка гарантированно снимается (fail-safe)."""
        patient = "Сбойный Пациент"
        with SYNC_LOCK:
            ACTIVE_PATIENT_SYNCS[patient] = {
                "status": "in_progress",
                "patient_folder": patient
            }

        with patch("main.sync_patient_folder", side_effect=RuntimeError("Disk connection lost")):
            run_background_patient_sync(patient, batch_limit=25, pause_seconds=0.01)

        with SYNC_LOCK:
            self.assertNotIn(patient, ACTIVE_PATIENT_SYNCS)

    def test_status_endpoint_idle_and_in_progress(self):
        """9. Эндпоинт GET /api/v1/sync/patient/{patient_folder} отображает idle и in_progress."""
        patient = "Иванов Иван"

        # 9.1 Статус до старта: idle
        res1 = self.client.get(f"/api/v1/sync/patient/{patient}", headers=self.patient1_headers)
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json().get("status"), "idle")
        self.assertFalse(res1.json().get("is_syncing"))

        # 9.2 Статус во время активности
        with SYNC_LOCK:
            ACTIVE_PATIENT_SYNCS[patient] = {
                "status": "in_progress",
                "started_at": "2026-09-25T10:00:00",
                "patient_folder": patient
            }

        res2 = self.client.get(f"/api/v1/sync/patient/{patient}", headers=self.patient1_headers)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json().get("status"), "in_progress")
        self.assertTrue(res2.json().get("is_syncing"))

    def test_admin_get_all_active_syncs(self):
        """10. Администратор видит список всех активных синхронизаций через GET /api/v1/sync/active."""
        with SYNC_LOCK:
            ACTIVE_PATIENT_SYNCS["Пациент 1"] = {"patient_folder": "Пациент 1", "status": "in_progress"}
            ACTIVE_PATIENT_SYNCS["Пациент 2"] = {"patient_folder": "Пациент 2", "status": "in_progress"}

        res = self.client.get("/api/v1/sync/active", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("count"), 2)
        self.assertEqual(len(data.get("active_syncs", [])), 2)

if __name__ == "__main__":
    unittest.main()
