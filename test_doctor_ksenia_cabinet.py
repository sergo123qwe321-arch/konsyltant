# -*- coding: utf-8 -*-
import test_bootstrap
"""
Тесты изоляции кабинета врача Ксении Корякиной (Этап 5, шаг 5.2):
идемпотентный сид, логин + payload JWT, изолированность клинических заметок.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fastapi.testclient import TestClient  # noqa: E402

import database  # noqa: E402
from main import app  # noqa: E402
from security_utils import verify_token  # noqa: E402

KSENIA_EMAIL = "ksenia.koryakina@cmz.site"
KSENIA_LICENSE = "DOC-KSENIA-001"
KSENIA_PASSWORD = "KseniaTherapist2026!"
KSENIA_NAME = "Ксения Александровна Корякина"
KSENIA_SPECIALTY = "Терапевт"

ISOLATION_FOLDER = "folder_test_ksenia_isolation"
ISOLATION_EMAIL = "doc_isolation_test_ksenia@cmz.site"
ISOLATION_LICENSE = "DOC-KSENIA-ISOL-TEST"


def _query_one(sql, params=()):
    conn = database.get_connection()
    cursor = conn.cursor()
    database.execute_query(cursor, sql, params)
    row = cursor.fetchone()
    conn.close()
    return row


def _query_all(sql, params=()):
    conn = database.get_connection()
    cursor = conn.cursor()
    database.execute_query(cursor, sql, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


class KseniaCabinetTests(unittest.TestCase):
    """Кабинет Ксении: сид, аутентификация и изоляция заметок."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # init_db() уже выполнен при импорте main → сид отработал;
        # страховой повторный вызов подтверждает идемпотентность
        database.seed_doctor_ksenia()

    @classmethod
    def tearDownClass(cls):
        # Гигиена: не оставляем тестовые данные в БД (урок загрязнения из аудита 5.1)
        conn = database.get_connection()
        cursor = conn.cursor()
        database.execute_query(
            cursor, "DELETE FROM doctor_notes WHERE patient_folder_id = ?", (ISOLATION_FOLDER,)
        )
        database.execute_query(
            cursor, "DELETE FROM doctors WHERE license_number = ?", (ISOLATION_LICENSE,)
        )
        conn.commit()
        conn.close()

    def test_ksenia_account_seeded(self):
        """Врач Ксения засеян: ФИО, специальность 'Терапевт', verified, role=DOCTOR."""
        row = _query_one(
            "SELECT id, full_name, specialty, is_verified, role "
            "FROM doctors WHERE email = ? OR license_number = ?",
            (KSENIA_EMAIL, KSENIA_LICENSE),
        )
        self.assertIsNotNone(row, "Профиль Ксении должен существовать в БД")
        doc_id, full_name, specialty, is_verified, role = row
        self.assertEqual(full_name, KSENIA_NAME)
        self.assertEqual(specialty, KSENIA_SPECIALTY)
        self.assertTrue(bool(is_verified), "Врач должен быть верифицирован")
        self.assertEqual(role, "DOCTOR")

        # Идемпотентность: повторный сид не создаёт дубликатов
        count_before = _query_one(
            "SELECT COUNT(*) FROM doctors WHERE email = ? OR license_number = ?",
            (KSENIA_EMAIL, KSENIA_LICENSE),
        )[0]
        database.seed_doctor_ksenia()
        count_after = _query_one(
            "SELECT COUNT(*) FROM doctors WHERE email = ? OR license_number = ?",
            (KSENIA_EMAIL, KSENIA_LICENSE),
        )[0]
        self.assertEqual(count_before, 1)
        self.assertEqual(count_after, 1)
        self.assertGreater(doc_id, 0)

    def test_ksenia_login_and_jwt_payload(self):
        """Логин по email + стартовому паролю: 200, bearer, payload JWT."""
        row = _query_one("SELECT id FROM doctors WHERE email = ?", (KSENIA_EMAIL,))
        self.assertIsNotNone(row, "Врач Ксении должен существовать до логина")
        ksenia_id = row[0]

        resp = self.client.post(
            "/api/v1/doctor/login",
            json={"login": KSENIA_EMAIL, "password": KSENIA_PASSWORD},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["doctor_id"], ksenia_id)
        self.assertEqual(data["full_name"], KSENIA_NAME)
        self.assertEqual(data["specialty"], KSENIA_SPECIALTY)

        payload = verify_token(data["access_token"])
        self.assertIsNotNone(payload, "JWT должен быть валидным")
        self.assertEqual(payload.get("role"), "DOCTOR")
        self.assertEqual(payload.get("full_name"), KSENIA_NAME)
        self.assertEqual(payload.get("specialty"), KSENIA_SPECIALTY)
        self.assertEqual(payload.get("doctor_id"), ksenia_id)
        self.assertEqual(payload.get("sub"), str(ksenia_id))

    def test_ksenia_cabinet_notes_isolation(self):
        """Заметки Ксении привязаны к её doctor_id и изолированы от другого врача."""
        ksenia = _query_one("SELECT id FROM doctors WHERE email = ?", (KSENIA_EMAIL,))
        self.assertIsNotNone(ksenia)
        ksenia_id = ksenia[0]

        # Второй специалист для проверки изоляции
        other = database.create_doctor(
            full_name="Доктор Изоляции Кабинета",
            specialty="Тестовый специалист",
            license_number=ISOLATION_LICENSE,
            is_verified=False,
            email=ISOLATION_EMAIL,
            password_hash=None,
        )
        other_id = other["id"]
        self.assertNotEqual(ksenia_id, other_id)

        # Токены обоих врачей
        r_ksenia = self.client.post(
            "/api/v1/doctor/login",
            json={"login": KSENIA_EMAIL, "password": KSENIA_PASSWORD},
        )
        self.assertEqual(r_ksenia.status_code, 200)
        token_ksenia = r_ksenia.json()["access_token"]

        r_other = self.client.post(
            "/api/v1/doctor/login",
            json={"login": ISOLATION_EMAIL, "password": "doctor123"},
        )
        self.assertEqual(r_other.status_code, 200)
        token_other = r_other.json()["access_token"]
        self.assertEqual(r_other.json()["doctor_id"], other_id)

        # Каждый врач сохраняет свою заметку по одной и той же папке пациента
        url = f"/api/v1/doctor/patient/{ISOLATION_FOLDER}/notes"
        save_k = self.client.post(
            url, json={"note_text": "Заметка Ксении"}, headers={"Authorization": f"Bearer {token_ksenia}"}
        )
        self.assertEqual(save_k.status_code, 200)
        self.assertEqual(save_k.json()["note"]["doctor_id"], ksenia_id)

        save_o = self.client.post(
            url, json={"note_text": "Заметка другого врача"}, headers={"Authorization": f"Bearer {token_other}"}
        )
        self.assertEqual(save_o.status_code, 200)
        self.assertEqual(save_o.json()["note"]["doctor_id"], other_id)

        # Каждый видит только свою заметку
        get_k = self.client.get(url, headers={"Authorization": f"Bearer {token_ksenia}"})
        self.assertEqual(get_k.status_code, 200)
        self.assertEqual(get_k.json()["note"]["note_text"], "Заметка Ксении")

        get_o = self.client.get(url, headers={"Authorization": f"Bearer {token_other}"})
        self.assertEqual(get_o.status_code, 200)
        self.assertEqual(get_o.json()["note"]["note_text"], "Заметка другого врача")

        # В БД по папке две изолированные строки с разными doctor_id
        rows = _query_all(
            "SELECT doctor_id, note_text FROM doctor_notes WHERE patient_folder_id = ?",
            (ISOLATION_FOLDER,),
        )
        by_doctor = {r[0]: r[1] for r in rows}
        self.assertEqual(by_doctor.get(ksenia_id), "Заметка Ксении")
        self.assertEqual(by_doctor.get(other_id), "Заметка другого врача")


if __name__ == "__main__":
    unittest.main()
