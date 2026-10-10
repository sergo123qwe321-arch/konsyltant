import unittest

from fastapi.testclient import TestClient

from main import app
from database import get_public_posts, get_public_library_items

client = TestClient(app)


class TestArticleRoutes(unittest.TestCase):
    """Автотесты маршрутизации автономных SSR-страниц статей и материалов (Этап 3, шаг 3.3)."""

    @classmethod
    def setUpClass(cls):
        # Существующие записи из БД (пост ID 27 и материал ID 1 — по данным сидов)
        posts = get_public_posts()
        cls.post_id = posts[0]["id"] if posts else None
        items = get_public_library_items()
        cls.library_id = items[0]["id"] if items else None

    def test_post_page_status_200(self):
        """Существующий пост отдает 200 с OG-тегами, article.css и без app.js."""
        self.assertIsNotNone(self.post_id, "В БД должен существовать хотя бы один пост")
        res = client.get(f"/post/{self.post_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn('<link rel="stylesheet" href="/static/css/article.css"', res.text)
        self.assertIn("og:title", res.text)
        self.assertIn("og:description", res.text)
        self.assertIn('property="og:type" content="article"', res.text)
        self.assertNotIn("static/js/app.js", res.text)

    def test_post_page_404_not_found(self):
        """Несуществующий ID поста возвращает 404."""
        res = client.get("/post/999999999")
        self.assertEqual(res.status_code, 404)

    def test_post_page_422_invalid_id(self):
        """Невалидный тип ID поста возвращает 422."""
        res = client.get("/post/abc")
        self.assertEqual(res.status_code, 422)

    def test_library_page_status_200(self):
        """Существующий материал библиотеки отдает 200 с категорией и ссылкой на главную."""
        self.assertIsNotNone(self.library_id, "В БД должен существовать хотя бы один материал библиотеки")
        res = client.get(f"/library/{self.library_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("meta-badge-category", res.text)
        self.assertIn('class="back-link"', res.text)
        self.assertIn("← На главную", res.text)
        self.assertNotIn("static/js/app.js", res.text)

    def test_library_page_404_not_found(self):
        """Несуществующий ID материала библиотеки возвращает 404."""
        res = client.get("/library/999999999")
        self.assertEqual(res.status_code, 404)

    def test_article_css_status_200(self):
        """Автономный stylesheet статьи доступен по /static/css/article.css."""
        res = client.get("/static/css/article.css")
        self.assertEqual(res.status_code, 200)
        self.assertIn("article-body", res.text)


if __name__ == "__main__":
    unittest.main()
