# -*- coding: utf-8 -*-
import test_bootstrap
"""
Тесты учетной записи администратора Светланы (Этап 6, шаг 6.2):
идемпотентный сид в patient_access, логин /api/v1/admin/login и доступ
к защищенному административному API.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fastapi.testclient import TestClient  # noqa: E402

import database  # noqa: E402
from main import app  # noqa: E402
from security_utils import verify_token  # noqa: E402

SVETLANA_LOGIN = "svetlana"
SVETLANA_PASSWORD = "svetlanadefmarshryt123"
SVETLANA_FULL_NAME = "дефектолог Светлана / руководитель платформы Маршрут"
SVETLANA_SPECIALIZATION = "Дефектолог / Руководитель платформы"


def _query_one(sql, params=()):
    conn = database.get_connection()
    cursor = conn.cursor()
    database.execute_query(cursor, sql, params)
    row = cursor.fetchone()
    conn.close()
    return row


def _count_svetlana():
    return _query_one(
        "SELECT COUNT(*) FROM patient_access WHERE access_token = ? AND role = 'ADMIN'",
        (SVETLANA_LOGIN,),
    )[0]


class SvetlanaAdminCabinetTests(unittest.TestCase):
    """Кабинет администраторы Светланы: сид, логин и доступ к админ-API."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # init_db() уже выполнен при импорте main → сид отработал
        database.seed_admin_svetlana()

    def test_svetlana_account_seeded(self):
        """Запись Светланы в patient_access: роль, логин, ФИО; init_db идемпотентен."""
        row = _query_one(
            "SELECT id, access_token, role, is_verified, full_name, specialization, gdrive_folder_id "
            "FROM patient_access WHERE access_token = ? AND role = 'ADMIN'",
            (SVETLANA_LOGIN,),
        )
        self.assertIsNotNone(row, "Учетная запись Светланы должна существовать в БД")
        admin_id, login, role, is_verified, full_name, specialization, vault = row
        self.assertEqual(login, SVETLANA_LOGIN)
        self.assertEqual(role, "ADMIN")
        self.assertTrue(bool(is_verified), "Запись должна быть верифицирована")
        self.assertEqual(full_name, SVETLANA_FULL_NAME)
        self.assertEqual(specialization, SVETLANA_SPECIALIZATION)
        self.assertEqual(vault, "admin_vault")
        self.assertGreater(admin_id, 0)

        # Идемпотентность: повторный init_db() не плодит дубликатов
        count_before = _count_svetlana()
        database.init_db()
        count_after = _count_svetlana()
        self.assertEqual(count_before, 1)
        self.assertEqual(count_after, 1)

    def test_svetlana_login_success(self):
        """POST /api/v1/admin/login: 200, bearer, валидный JWT и full_name в ответе."""
        resp = self.client.post(
            "/api/v1/admin/login",
            json={"username": SVETLANA_LOGIN, "password": SVETLANA_PASSWORD},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["role"], "ADMIN")
        self.assertEqual(data["username"], SVETLANA_LOGIN)
        # Персонализация (Этап 6, шаг 6.3): отображаемое имя в ответе логина
        self.assertEqual(data.get("full_name"), SVETLANA_FULL_NAME)

        payload = verify_token(data["access_token"])
        self.assertIsNotNone(payload, "JWT должен быть валидным")
        self.assertEqual(payload.get("role"), "ADMIN")
        self.assertEqual(payload.get("sub"), SVETLANA_LOGIN)
        self.assertEqual(payload.get("allowed_folder"), "admin_vault")
        # Имя продублировано в payload JWT (для персонализации шапки)
        self.assertEqual(payload.get("full_name"), SVETLANA_FULL_NAME)

    def test_svetlana_admin_api_access(self):
        """Токен Светланы открывает защищенный админ-эндпоинт (GET /api/v1/admin/leads)."""
        r_login = self.client.post(
            "/api/v1/admin/login",
            json={"username": SVETLANA_LOGIN, "password": SVETLANA_PASSWORD},
        )
        self.assertEqual(r_login.status_code, 200)
        token = r_login.json()["access_token"]

        resp = self.client.get(
            "/api/v1/admin/leads", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(resp.status_code, 200)

        # Дополнительно: список специалистов тоже доступен
        resp_docs = self.client.get(
            "/api/v1/admin/doctors", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(resp_docs.status_code, 200)

        # Без токена тот же эндпоинт закрыт (401)
        resp_noauth = self.client.get("/api/v1/admin/leads")
        self.assertEqual(resp_noauth.status_code, 401)


if __name__ == "__main__":
    unittest.main()
