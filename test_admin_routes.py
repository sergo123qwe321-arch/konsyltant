import unittest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestAdminRoutes(unittest.TestCase):
    """Автотесты маршрутизации автономной панели /admin (Этап 2, шаг 2.4)."""

    def test_admin_page_status_200(self):
        """GET /admin и /admin/ отдают 200 с ключевыми маркерами автономной панели."""
        for url in ("/admin", "/admin/"):
            res = client.get(url)
            self.assertEqual(res.status_code, 200, f"{url} must return 200")
            self.assertIn("admin-root", res.text)
            self.assertIn("/static/css/admin.css", res.text)
            self.assertIn("/static/js/admin.js", res.text)

    def test_landing_has_no_admin_modals(self):
        """GET / больше не содержит демонтированных админ-модалок."""
        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("#admin-dashboard-modal", res.text)
        self.assertNotIn("#admin-login-modal", res.text)
        self.assertNotIn('id="admin-login-modal"', res.text)
        self.assertNotIn('id="admin-dashboard-modal"', res.text)
        self.assertNotIn("openAdminModal()", res.text)

    def test_landing_links_point_to_admin_route(self):
        """Точки входа панели на лендинге ведут на прямую ссылку /admin."""
        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn('href="/admin"', res.text)


if __name__ == "__main__":
    unittest.main()
