import unittest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestDoctorRoutes(unittest.TestCase):
    """Автотесты маршрутизации автономного кабинета /doctor (Этап 1, шаг 2.2)."""

    def test_doctor_page_status_200(self):
        """GET /doctor и /doctor/ отдают 200 с ключевыми маркерами автономного кабинета."""
        for url in ("/doctor", "/doctor/"):
            res = client.get(url)
            self.assertEqual(res.status_code, 200, f"{url} must return 200")
            self.assertIn("doctor-root", res.text)
            self.assertIn("/static/css/doctor.css", res.text)
            self.assertIn("/static/js/doctor.js", res.text)

    def test_landing_redirects_on_share_token(self):
        """GET /?share_token=... редиректит (307) в автономный кабинет /doctor."""
        res = client.get("/?share_token=test_token_123", follow_redirects=False)
        self.assertEqual(res.status_code, 307)
        self.assertEqual(res.headers["location"], "/doctor/?share_token=test_token_123")

    def test_landing_loads_normally_without_token(self):
        """Обычный GET / отдает лендинг 200 без редиректов."""
        res = client.get("/", follow_redirects=False)
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
