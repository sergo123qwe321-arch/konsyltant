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


if __name__ == "__main__":
    unittest.main()
