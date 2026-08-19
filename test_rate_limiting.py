import unittest
import time
from fastapi.testclient import TestClient
from main import app, auth_rate_limiter
from database import init_db

client = TestClient(app)

class TestAuthRateLimiting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        auth_rate_limiter.clear_all()

    def tearDown(self):
        auth_rate_limiter.clear_all()

    def test_rate_limit_allows_normal_usage(self):
        """1. До 4-х последовательных запросов проходят без блокировки 429."""
        test_ip = "203.0.113.10"
        headers = {"X-Forwarded-For": test_ip}

        for i in range(4):
            res = client.post("/api/v1/doctor/login", json={
                "login": "doc_anna",
                "password": "wrong_pass"
            }, headers=headers)
            self.assertEqual(res.status_code, 401, f"Request {i+1} should return 401, not 429")

    def test_rate_limit_blocks_excessive_requests(self):
        """2. 6-й запрос в течение минуты возвращает HTTP 429 Too Many Requests."""
        test_ip = "203.0.113.20"
        headers = {"X-Forwarded-For": test_ip}

        # 5 неудачных попыток
        for i in range(5):
            res = client.post("/api/v1/doctor/login", json={
                "login": "doc_anna",
                "password": "wrong_pass"
            }, headers=headers)
            self.assertEqual(res.status_code, 401)

        # 6-й запрос блокируется
        res_blocked = client.post("/api/v1/doctor/login", json={
            "login": "doc_anna",
            "password": "wrong_pass"
        }, headers=headers)
        self.assertEqual(res_blocked.status_code, 429)
        data = res_blocked.json()
        self.assertIn("detail", data)
        self.assertIn("Превышено количество попыток входа", data["detail"])
        self.assertIn("retry_after", data)
        self.assertGreater(data["retry_after"], 0)

    def test_rate_limit_resets_after_time(self):
        """3. После истечения окна блокировки лимит сбрасывается."""
        test_ip = "203.0.113.30"
        headers = {"X-Forwarded-For": test_ip}

        # Симулируем 5 попыток в прошлом (65 секунд назад)
        past_time = time.time() - 65
        auth_rate_limiter.attempts[test_ip] = [past_time] * 5

        # Запрос должен пройти
        res = client.post("/api/v1/admin/login", json={
            "username": "admin",
            "password": "wrong_pass"
        }, headers=headers)
        self.assertEqual(res.status_code, 401)

    def test_rate_limit_only_applies_to_auth_endpoints(self):
        """4. Не-auth endpoints (GET публичные, сбор лидов) не блокируются rate limiter'ом."""
        test_ip = "203.0.113.40"
        headers = {"X-Forwarded-For": test_ip}

        # Делаем 10 запросов к публичным эндпоинтам
        for _ in range(10):
            res = client.get("/api/v1/public/services", headers=headers)
            self.assertEqual(res.status_code, 200)

            res_posts = client.get("/api/v1/public/posts", headers=headers)
            self.assertEqual(res_posts.status_code, 200)

    def test_rate_limit_resets_on_success(self):
        """5. Успешная авторизация (HTTP 200) сбрасывает счетчик попыток для данного IP."""
        test_ip = "203.0.113.50"
        headers = {"X-Forwarded-For": test_ip}

        # 3 неудачные попытки
        for _ in range(3):
            res = client.post("/api/v1/doctor/login", json={
                "login": "doc_anna",
                "password": "wrong_pass"
            }, headers=headers)
            self.assertEqual(res.status_code, 401)

        # 4-я попытка успешная
        res_ok = client.post("/api/v1/doctor/login", json={
            "login": "doc_anna",
            "password": "doctor123"
        }, headers=headers)
        self.assertEqual(res_ok.status_code, 200)

        # Проверяем, что счетчик сброшен (можно сделать еще 4 попытки без блокировки 429)
        for _ in range(4):
            res = client.post("/api/v1/doctor/login", json={
                "login": "doc_anna",
                "password": "wrong_pass"
            }, headers=headers)
            self.assertEqual(res.status_code, 401)

    def test_rate_limit_returns_retry_after_header(self):
        """6. Ответ 429 содержит корректный заголовок Retry-After."""
        test_ip = "203.0.113.60"
        headers = {"X-Forwarded-For": test_ip}

        # Превышаем лимит (5 попыток)
        for _ in range(5):
            client.post("/api/v1/admin/login", json={
                "username": "admin",
                "password": "wrong_pass"
            }, headers=headers)

        res_429 = client.post("/api/v1/admin/login", json={
            "username": "admin",
            "password": "wrong_pass"
        }, headers=headers)

        self.assertEqual(res_429.status_code, 429)
        self.assertIn("retry-after", res_429.headers)
        retry_val = int(res_429.headers["retry-after"])
        self.assertGreater(retry_val, 0)
        self.assertLessEqual(retry_val, 300)

if __name__ == '__main__':
    unittest.main()

