import unittest
import os
import re
from fastapi.testclient import TestClient
from main import app
from database import init_db, get_connection, execute_query
from security_utils import create_access_token
from scripts.admin.seed_producer_admin import seed_producer_admin

class TestLandingAndAdminOps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        # Сидируем админа
        seed_producer_admin()
        
        cls.admin_token = create_access_token({"sub": "producer-admin@cmz.site", "role": "ADMIN"})
        cls.doctor_token = create_access_token({"sub": "doc_anna", "role": "DOCTOR"})
        cls.patient_token = create_access_token({"sub": "test_patient", "role": "PATIENT"})

    def test_01_landing_sections_order(self):
        """1. Проверка порядка секций лендинга в templates/index.html"""
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        pos_hero = html.find('id="hero"')
        pos_posts = html.find('id="posts"')
        pos_blog = html.find('id="blog"')
        pos_characters = html.find('id="characters"')
        pos_about = html.find('id="about"')
        pos_services = html.find('id="services"')
        pos_doctors = html.find('id="doctors"')
        pos_events = html.find('id="events"')
        pos_contacts = html.find('id="contacts"')
        pos_footer = html.find('<footer')

        self.assertNotEqual(pos_hero, -1, "Hero секция найдена")
        self.assertNotEqual(pos_posts, -1, "Секция Новые посты найдена")
        self.assertNotEqual(pos_blog, -1, "Секция Полезная библиотека найдена")
        self.assertNotEqual(pos_characters, -1, "Секция Персонажи звуков найдена")
        self.assertNotEqual(pos_about, -1, "Секция О центре найдена")
        self.assertNotEqual(pos_services, -1, "Секция Услуги найдена")
        self.assertNotEqual(pos_doctors, -1, "Секция Врачи найдена")
        self.assertNotEqual(pos_events, -1, "Секция События найдена")
        self.assertNotEqual(pos_contacts, -1, "Секция Контакты найдена")
        self.assertNotEqual(pos_footer, -1, "Подвал найден")

        # Проверяем строгий порядок
        self.assertTrue(pos_hero < pos_posts, "Hero должен идти перед Новыми постами")
        self.assertTrue(pos_posts < pos_blog, "Новые посты должны идти перед Библиотекой")
        self.assertTrue(pos_blog < pos_characters, "Библиотека должна идти перед Персонажами звуков")
        self.assertTrue(pos_characters < pos_about, "Персонажи должны идти перед О центре")
        self.assertTrue(pos_about < pos_services, "О центре перед Услугами")
        self.assertTrue(pos_services < pos_doctors, "Услуги перед Врачами")
        self.assertTrue(pos_doctors < pos_events, "Врачи перед Событиями")
        self.assertTrue(pos_events < pos_contacts, "События перед Контактами")
        self.assertTrue(pos_contacts < pos_footer, "Контакты перед Подвалом")

    def test_02_no_word_muzykalnaya_in_hero_and_seo(self):
        """2. Проверка отсутствия слова «музыкальная» в title, meta и hero"""
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        # Title
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        self.assertIsNotNone(title_match)
        self.assertNotIn("музыкальн", title_match.group(1).lower())
        self.assertIn("детская вселенная: маленькая страна", title_match.group(1).lower())

        # Meta description
        meta_desc = re.search(r'<meta\s+name="description"\s+content="(.*?)"', html, re.IGNORECASE)
        if meta_desc:
            self.assertNotIn("музыкальн", meta_desc.group(1).lower())
            self.assertIn("детская вселенная", meta_desc.group(1).lower())

        # Hero badge & H1
        hero_section = html[html.find('id="hero"'):html.find('id="posts"')]
        self.assertNotIn("музыкальная", hero_section.lower())
        self.assertIn("детская вселенная: маленькая страна", hero_section.lower())

    def test_03_end_to_end_post_publication(self):
        """3. Сквозная публикация поста: создание в CMS -> появление в публичных постах"""
        post_data = {
            "title": "Тестовая статья Продюсера о развитии внимания",
            "summary": "Краткое описание инновационной методики концентрации внимания у дошкольников.",
            "content": "Полный текст статьи с упражнениями для родителей и специалистов центра.",
            "tags": ["Эмоции и поведение", "Игры"]
        }

        # 1. Создание через Admin API
        res_create = self.client.post(
            "/api/v1/admin/posts",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=post_data
        )
        self.assertEqual(res_create.status_code, 200)

        # 2. Проверка в публичном API (должен быть первым в списке по created_at DESC)
        res_public = self.client.get("/api/v1/public/posts")
        self.assertEqual(res_public.status_code, 200)
        posts = res_public.json()
        self.assertTrue(len(posts) > 0)
        latest_post = posts[0]
        self.assertEqual(latest_post["title"], post_data["title"])
        self.assertEqual(latest_post["summary"], post_data["summary"])

        # 3. Получение по ID
        post_id = latest_post["id"]
        res_single = self.client.get(f"/api/v1/public/posts/{post_id}")
        self.assertEqual(res_single.status_code, 200)
        self.assertEqual(res_single.json()["title"], post_data["title"])

    def test_04_idempotent_admin_seed(self):
        """4. Идемпотентность сидирования админа и успешный логин"""
        # Повторный запуск сидирования
        seed_producer_admin()
        seed_producer_admin()

        conn = get_connection()
        cursor = conn.cursor()
        execute_query(cursor, "SELECT COUNT(*) FROM patient_access WHERE access_token = 'producer-admin@cmz.site';")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1, "Должна быть ровно 1 запись с данным логином")

        # Проверка логина через эндпоинт
        res_login = self.client.post(
            "/api/v1/admin/login",
            json={"username": "producer-admin@cmz.site", "password": "AdminAccess2026!"}
        )
        self.assertEqual(res_login.status_code, 200)
        data = res_login.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "ADMIN")

    def test_05_rbac_operational_endpoints(self):
        """5. Проверка RBAC для операционных эндпоинтов (401 без токена, 403 для PATIENT/DOCTOR, 200 для ADMIN)"""
        endpoints = [
            "/api/v1/admin/etl/metrics",
            "/api/v1/admin/llm/usage",
            "/api/v1/health/yandex-disk"
        ]

        for ep in endpoints:
            # Без токена -> 401
            res_anon = self.client.get(ep)
            self.assertEqual(res_anon.status_code, 401, f"{ep} без токена должен быть 401")

            # Пациент -> 403
            res_patient = self.client.get(ep, headers={"Authorization": f"Bearer {self.patient_token}"})
            self.assertEqual(res_patient.status_code, 403, f"{ep} для PATIENT должен быть 403")

            # Врач -> 403
            res_doctor = self.client.get(ep, headers={"Authorization": f"Bearer {self.doctor_token}"})
            self.assertEqual(res_doctor.status_code, 403, f"{ep} для DOCTOR должен быть 403")

            # Администратор -> 200
            res_admin = self.client.get(ep, headers={"Authorization": f"Bearer {self.admin_token}"})
            self.assertEqual(res_admin.status_code, 200, f"{ep} для ADMIN должен быть 200")

if __name__ == "__main__":
    unittest.main()

