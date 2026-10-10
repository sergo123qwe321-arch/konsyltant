# -*- coding: utf-8 -*-
"""
Тесты правовых дисклеймеров (Этап 7, шаг 7.1):
немедицинский статус платформы «Маршрут» на ключевых точках входа.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402

# Ключевая фраза Единого юридического дисклеймера
UNIFIED_MARKER = "не оказывает медицинских услуг"
UNIFIED_SCOPE = "вне рамок платформы"


class LegalDisclaimerTests(unittest.TestCase):
    """Наличие правовых дисклеймеров в ответах GET /, /doctor, /admin."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_landing_footer_unified_disclaimer(self):
        """GET /: Единый юридический дисклеймер в футере лендинга."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        body = resp.text
        self.assertIn(UNIFIED_MARKER, body)
        self.assertIn("Единый юридический дисклеймер", body)
        self.assertIn("информационно-навигационным сервисом", body)
        self.assertIn(UNIFIED_SCOPE, body)

    def test_doctor_cabinet_legal_notice(self):
        """GET /doctor: плашка platform-legal-notice в кабинете специалиста."""
        resp = self.client.get("/doctor")
        self.assertEqual(resp.status_code, 200)
        body = resp.text
        self.assertIn('class="platform-legal-notice"', body)
        self.assertIn("Платформа «Маршрут» носит информационно-навигационный характер", body)
        self.assertIn(UNIFIED_SCOPE, body)

    def test_admin_registration_terms_checkbox(self):
        """GET /admin: дисклеймер и обязательный чекбокс в форме регистрации специалиста."""
        resp = self.client.get("/admin")
        self.assertEqual(resp.status_code, 200)
        body = resp.text
        # Обязательный чекбокс согласия
        self.assertIn('id="doc-reg-terms"', body)
        self.assertIn('type="checkbox" id="doc-reg-terms" required', body)
        # Текст согласия и дисклеймер формы
        self.assertIn("Специалист уведомлен о немедицинском статусе платформы", body)
        self.assertIn(UNIFIED_MARKER, body)
        self.assertIn("информационно-навигационным сервисом", body)


if __name__ == "__main__":
    unittest.main()
