import unittest
import os
import re
import io
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
        """1. Проверка порядка секций лендинга в templates/index.html: Посты первыми, выше Hero!"""
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        pos_posts = html.find('id="posts"')
        pos_hero = html.find('id="hero"')
        pos_blog = html.find('id="blog"')
        pos_characters = html.find('id="characters"')
        pos_about = html.find('id="about"')
        pos_services = html.find('id="services"')
        pos_doctors = html.find('id="doctors"')
        pos_events = html.find('id="events"')
        pos_contacts = html.find('id="contacts"')
        pos_footer = html.find('<footer')

        self.assertNotEqual(pos_posts, -1, "Секция Новые посты найдена")
        self.assertNotEqual(pos_hero, -1, "Hero секция найдена")
        self.assertNotEqual(pos_blog, -1, "Секция Полезная библиотека найдена")
        self.assertNotEqual(pos_characters, -1, "Секция Персонажи звуков найдена")
        self.assertNotEqual(pos_about, -1, "Секция О центре найдена")
        self.assertNotEqual(pos_services, -1, "Секция Услуги найдена")
        self.assertNotEqual(pos_doctors, -1, "Секция Врачи найдена")
        self.assertNotEqual(pos_events, -1, "Секция События найдена")
        self.assertNotEqual(pos_contacts, -1, "Секция Контакты найдена")
        self.assertNotEqual(pos_footer, -1, "Подвал найден")

        # Проверяем строгий порядок: Посты -> Hero -> Библиотека -> Персонажи -> О центре -> Услуги -> Врачи -> События -> Контакты -> Подвал
        self.assertTrue(pos_posts < pos_hero, "Новые посты должны идти САМЫМИ ПЕРВЫМИ, перед Hero")
        self.assertTrue(pos_hero < pos_blog, "Hero должен идти перед Библиотекой")
        self.assertTrue(pos_blog < pos_characters, "Библиотека должна идти перед Персонажами звуков")
        self.assertTrue(pos_characters < pos_about, "Персонажи должны идти перед О центре")
        self.assertTrue(pos_about < pos_services, "О центре перед Услугами")
        self.assertTrue(pos_services < pos_doctors, "Услуги перед Врачами")
        self.assertTrue(pos_doctors < pos_events, "Врачи перед Событиями")
        self.assertTrue(pos_events < pos_contacts, "События перед Контактами")
        self.assertTrue(pos_contacts < pos_footer, "Контакты перед Подвалом")

    def test_02_no_word_muzykalnaya_and_klinika(self):
        """2. Проверка отсутствия запрещенных слов («музыкальная», «клиника») в UI и SEO"""
        with open("templates/index.html", "r", encoding="utf-8") as f:
            html = f.read()

        # Title
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        self.assertIsNotNone(title_match)
        self.assertNotIn("музыкальн", title_match.group(1).lower())
        self.assertNotIn("клиник", title_match.group(1).lower())
        self.assertIn("детская вселенная: маленькая страна", title_match.group(1).lower())

        # Hero badge & H1
        hero_section = html[html.find('id="hero"'):html.find('id="blog"')]
        self.assertNotIn("музыкальная", hero_section.lower())
        self.assertNotIn("клиника", hero_section.lower())
        self.assertIn("детская вселенная: маленькая страна", hero_section.lower())

    def test_03_end_to_end_post_publication_with_multimedia(self):
        """3. Создание поста с мультимедиа (обложка, видео) через Admin API и проверка в Public API"""
        post_data = {
            "title": "Интерактивные упражнения для развития речи",
            "summary": "Методические рекомендации и видеоматериалы от ведущих специалистов Центра.",
            "content": "Подробный разбор артикуляционной гимнастики и игровых методик в домашних условиях.",
            "tags": ["Развитие речи", "Игры"],
            "cover_image_url": "https://disk.yandex.ru/i/test_speech_cover.jpg",
            "video_url": "https://disk.yandex.ru/i/test_speech_video.mp4",
            "attachments": [{"title": "Памятка для родителей (PDF)", "url": "https://disk.yandex.ru/d/manual.pdf"}]
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
        self.assertEqual(latest_post["cover_image_url"], post_data["cover_image_url"])
        self.assertEqual(latest_post["video_url"], post_data["video_url"])

        # 3. Получение по ID
        post_id = latest_post["id"]
        res_single = self.client.get(f"/api/v1/public/posts/{post_id}")
        self.assertEqual(res_single.status_code, 200)
        self.assertEqual(res_single.json()["title"], post_data["title"])
        self.assertEqual(res_single.json()["cover_image_url"], post_data["cover_image_url"])

    def test_04_admin_media_url_validation_endpoint(self):
        """4. Валидация внешнего URL через эндпоинт POST /api/v1/admin/media-url"""
        valid_payload = {
            "url": "https://rutube.ru/video/123456/",
            "type": "video"
        }
        res_valid = self.client.post(
            "/api/v1/admin/media-url",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=valid_payload
        )
        self.assertEqual(res_valid.status_code, 200)
        data = res_valid.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["validated_url"], valid_payload["url"])

        # Проверка отклонения неразрешенных доменов
        invalid_payload = {
            "url": "https://untrusted-unknown-site.net/watch?v=123",
            "type": "video"
        }
        res_invalid = self.client.post(
            "/api/v1/admin/media-url",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=invalid_payload
        )
        self.assertEqual(res_invalid.status_code, 400)

    def test_05_admin_leads_endpoint(self):
        """5. Получение списка заявок через GET /api/v1/admin/leads"""
        res_leads = self.client.get(
            "/api/v1/admin/leads",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res_leads.status_code, 200)
        leads = res_leads.json()
        self.assertIsInstance(leads, list)

    def test_06_public_library_crud(self):
        """6. Создание и получение материалов полезной библиотеки"""
        lib_data = {
            "title": "Сборник речевых сказок для малышей",
            "summary": "Аудиосказки и тексты для постановки звуков раннего онтогенеза.",
            "content": "Полный текст сказок и методические указания по чтению перед сном.",
            "category": "Развитие речи",
            "tags": ["Сказки", "Речь"],
            "cover_image_url": "https://disk.yandex.ru/i/tales_cover.png",
            "video_url": ""
        }

        res_create = self.client.post(
            "/api/v1/admin/library",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json=lib_data
        )
        self.assertEqual(res_create.status_code, 200)

        res_list = self.client.get("/api/v1/public/library")
        self.assertEqual(res_list.status_code, 200)
        items = res_list.json()
        self.assertTrue(len(items) > 0)
        self.assertEqual(items[0]["title"], lib_data["title"])

    def test_07_rbac_operational_endpoints(self):
        """7. Проверка RBAC для операционных эндпоинтов (401 без токена, 403 для PATIENT/DOCTOR, 200 для ADMIN)"""
        endpoints = [
            "/api/v1/admin/etl/metrics",
            "/api/v1/admin/llm/usage",
            "/api/v1/admin/health/yandex-disk",
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

