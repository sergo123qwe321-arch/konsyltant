# -*- coding: utf-8 -*-
"""
Интеграционные тесты офлайн-заглушки PWA (Этап 4, шаг 4.2):
GET /offline и GET /offline/ + ключевые маркеры страницы.
"""
import sys
import pathlib
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from fastapi.testclient import TestClient  # noqa: E402
import main  # noqa: E402
from database import get_public_posts  # noqa: E402

SW_REGISTRATION_MARKER = "navigator.serviceWorker.register('/sw.js'"


class OfflinePageTests(unittest.TestCase):
    """Маршрут /offline отдаёт изолированную Zero-JS страницу-заглушку."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_offline_page_status_200(self):
        """GET /offline и GET /offline/ возвращают 200 OK."""
        for path in ("/offline", "/offline/"):
            with self.subTest(path=path):
                resp = self.client.get(path)
                self.assertEqual(resp.status_code, 200)

    def test_offline_page_key_markers(self):
        """Тело содержит заголовок, кнопку ручного обновления и контакты Центра."""
        resp = self.client.get("/offline")
        self.assertEqual(resp.status_code, 200)
        body = resp.text
        # Ключевой заголовок состояния
        self.assertIn("Связь временно прервалась", body)
        # Кнопка ручного обновления (единственный JS на странице)
        self.assertIn("location.reload()", body)
        self.assertIn("btn-retry", body)
        # Экстренные контакты Центра: телефон Службы заботы и адрес
        self.assertIn("tel:+78125553322", body)
        self.assertIn("+7 (812) 555-33-22", body)
        self.assertIn("ул. Детских Открытий, дом 7", body)
        # Ссылка возврата на главную и метатеги
        self.assertIn('class="home-link" href="/"', body)
        self.assertIn("<title>Нет связи с сервером", body)
        self.assertIn('<html lang="ru">', body)

    def test_offline_page_is_self_contained(self):
        """Zero-JS: нет внешних скриптов/шрифтов, только автономный <style>."""
        resp = self.client.get("/offline")
        body = resp.text
        self.assertNotIn("<script", body)
        self.assertNotIn("fonts.googleapis.com", body)
        self.assertNotIn("/static/", body)
        self.assertIn("<style>", body)

    def test_service_worker_route_status_and_headers(self):
        """GET /sw.js: 200, application/javascript, scope / и антикэш-заголовки."""
        resp = self.client.get("/sw.js")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/javascript", resp.headers.get("content-type", ""))
        # Scope разрешает контроль всего сайта (/, /doctor, /admin, /post/*)
        self.assertEqual(resp.headers.get("service-worker-allowed"), "/")
        # Защита от кэширования SW-скрипта (Nginx/browser)
        cache_control = resp.headers.get("cache-control", "")
        self.assertIn("no-cache", cache_control)
        self.assertIn("no-store", cache_control)
        self.assertIn("must-revalidate", cache_control)
        self.assertEqual(resp.headers.get("pragma"), "no-cache")
        self.assertEqual(resp.headers.get("expires"), "0")
        # Тело: версионирование и precache оболочки
        body = resp.text
        self.assertIn("const CACHE_NAME = 'cmz-cache-v1'", body)
        self.assertIn("'/offline'", body)
        self.assertIn("'/static/css/style.css'", body)
        self.assertIn("skipWaiting", body)
        self.assertIn("clients.claim", body)

    def test_templates_contain_sw_registration(self):
        """Все оболочки (/, /doctor, /admin, /post/{id}) регистрируют /sw.js."""
        posts = get_public_posts()
        self.assertTrue(posts, "В БД должен существовать хотя бы один пост")
        routes = ["/", "/doctor", "/admin", f"/post/{posts[0]['id']}"]
        for route in routes:
            with self.subTest(route=route):
                resp = self.client.get(route)
                self.assertEqual(resp.status_code, 200)
                self.assertIn(SW_REGISTRATION_MARKER, resp.text)


if __name__ == "__main__":
    unittest.main()
