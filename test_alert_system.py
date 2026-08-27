"""
test_alert_system.py — Комплексный тестовый набор для подсистемы оповещений о сбоях,
дедупликации, recovery-уведомлений и аудита документации (process.md и ARCHITECTURE.md).
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Устанавливаем тестовое окружение без перезаписи боевого DATABASE_URL
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///test_alert_tmp.db"
if "ADMIN_SECRET_KEY" not in os.environ:
    os.environ["ADMIN_SECRET_KEY"] = "test_admin_secret_key_12345"
if "JWT_SECRET_KEY" not in os.environ:
    os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_12345"
if "PRIMARY_ALERT_EMAIL" not in os.environ:
    os.environ["PRIMARY_ALERT_EMAIL"] = "konsultantms@yandex.com"
if "SECONDARY_ALERT_EMAIL" not in os.environ:
    os.environ["SECONDARY_ALERT_EMAIL"] = "sergo123qwe321@gmail.com"

from main import app
from security_utils import create_access_token
import alert_service
from alert_service import (
    PRIMARY_ALERT_EMAIL,
    SECONDARY_ALERT_EMAIL,
    ALERT_STATES,
    send_dual_email,
    check_yandex_disk,
    check_gigachat_api,
    check_etl_worker,
    check_gigachat_token_balance,
    check_etl_performance,
    check_database_availability,
    check_backup_freshness,
    trigger_daily_backup_if_needed,
    run_health_checks_and_alert,
    send_test_alert,
    get_alert_recipients,
)


class TestDocumentationAudit(unittest.TestCase):
    """Тесты полноты и чистоты документации (process.md и ARCHITECTURE.md)."""

    def test_process_md_completeness(self):
        """Проверка наличия всех ключевых итераций и структуры в process.md."""
        process_path = os.path.join(os.path.dirname(__file__), "process.md")
        self.assertTrue(os.path.exists(process_path), "process.md должен существовать")
        
        with open(process_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Проверка обязательных итераций
        required_topics = [
            "Initial Audit",
            "Rate Limiting",
            "Performance",
            "Tech Sovereignty",
            "Auth Fix",
            "AI Clinical Summary",
            "ReportLab",
            "Sharing",
            "Google Drive",
            "ETL Diagnostic",
            "Observability",
            "CMS & UI",
            "Multimedia",
            "Alert System",
        ]
        for topic in required_topics:
            self.assertIn(
                topic.lower(),
                content.lower(),
                f"process.md должен содержать описание итерации: {topic}"
            )

        # Проверка наличия атрибута 'Затронутые файлы:'
        self.assertIn("Затронутые файлы:", content, "process.md должен содержать блоки 'Затронутые файлы:'")

    def test_architecture_md_cleanliness(self):
        """Проверка чистоты ARCHITECTURE.md (отсутствие Google Drive в техстеке, правильная терминология)."""
        arch_path = os.path.join(os.path.dirname(__file__), "ARCHITECTURE.md")
        self.assertTrue(os.path.exists(arch_path), "ARCHITECTURE.md должен существовать")
        
        with open(arch_path, "r", encoding="utf-8") as f:
            content = f.read()

        # В техстеке Google Drive не должен фигурировать
        self.assertNotIn("Google Drive API (резервный источник)", content)

        # Проверка терминологии "центр ментального здоровья"
        self.assertIn("Администратор центра ментального здоровья", content)
        self.assertNotIn("Администратор Клиники", content)

        # Проверка наличия раздела системы оповещений
        self.assertIn("Система оповещений о критических сбоях", content)
        self.assertIn("PRIMARY_ALERT_EMAIL=konsultantms@yandex.com", content)
        self.assertIn("SECONDARY_ALERT_EMAIL=sergo123qwe321@gmail.com", content)


class TestAlertSystem(unittest.TestCase):
    """Тесты подсистемы оповещений, проверки порогов, дедупликации и восстановления."""

    def setUp(self):
        self.client = TestClient(app)
        # Сброс состояния алертов перед каждым тестом
        ALERT_STATES.clear()

    def test_alert_recipients_configuration(self):
        """Проверка адресов получателей алертов."""
        recipients = get_alert_recipients()
        self.assertIn("konsultantms@yandex.com", recipients)
        self.assertIn("sergo123qwe321@gmail.com", recipients)
        self.assertEqual(len(recipients), 2)

    @patch("notification_service.NotificationService.send_smtp_email")
    def test_dual_email_delivery(self, mock_send_email):
        """Проверка отправки писем на оба адреса."""
        mock_send_email.return_value = True

        res = send_dual_email("Тестовая тема", "<h1>Тестовое тело</h1>")
        self.assertTrue(res.get("konsultantms@yandex.com"))
        self.assertTrue(res.get("sergo123qwe321@gmail.com"))
        self.assertEqual(mock_send_email.call_count, 2)

    @patch("alert_service.send_dual_email")
    def test_alert_deduplication(self, mock_dual_send):
        """Проверка механизма дедупликации (не чаще 1 раза в час при постоянном сбое)."""
        mock_dual_send.return_value = {"konsultantms@yandex.com": True, "sergo123qwe321@gmail.com": True}

        # Симулируем 1-ю проверку со сбоем
        with patch("alert_service.check_yandex_disk", return_value=(False, "Yandex Disk API 500 Error", "Status 500")):
            with patch("alert_service.check_gigachat_api", return_value=(True, "OK", "0")):
                with patch("alert_service.check_etl_worker", return_value=(True, "OK", "10s")):
                    with patch("alert_service.check_gigachat_token_balance", return_value=(True, "OK", "100%")):
                        with patch("alert_service.check_etl_performance", return_value=(True, "OK", "3.5s")):
                            with patch("alert_service.check_database_availability", return_value=(True, "OK", "connected")):
                                with patch("alert_service.check_backup_freshness", return_value=(True, "OK", "1.0 ч")):
                                    results1 = run_health_checks_and_alert()

        # Первое письмо должно быть отправлено
        self.assertEqual(mock_dual_send.call_count, 1)
        self.assertTrue(ALERT_STATES["yandex_disk"]["is_active"])

        # Симулируем 2-ю проверку сразу же (в течение того же часа)
        with patch("alert_service.check_yandex_disk", return_value=(False, "Yandex Disk API 500 Error", "Status 500")):
            with patch("alert_service.check_gigachat_api", return_value=(True, "OK", "0")):
                with patch("alert_service.check_etl_worker", return_value=(True, "OK", "10s")):
                    with patch("alert_service.check_gigachat_token_balance", return_value=(True, "OK", "100%")):
                        with patch("alert_service.check_etl_performance", return_value=(True, "OK", "3.5s")):
                            with patch("alert_service.check_database_availability", return_value=(True, "OK", "connected")):
                                with patch("alert_service.check_backup_freshness", return_value=(True, "OK", "1.0 ч")):
                                    results2 = run_health_checks_and_alert()

        # Второе письмо НЕ должно отправляться (дедупликация 3600с)
        self.assertEqual(mock_dual_send.call_count, 1)

    @patch("alert_service.send_dual_email")
    def test_alert_recovery_notification(self, mock_dual_send):
        """Проверка отправки recovery-уведомления при нормализации метрики."""
        mock_dual_send.return_value = {"konsultantms@yandex.com": True, "sergo123qwe321@gmail.com": True}

        # 1. Задаем активный сбой
        ALERT_STATES["database"] = {
            "is_active": True,
            "last_alert_time": 1000.0,
            "first_detected": 900.0,
            "last_value": "timeout",
            "description": "DB Connection Timeout"
        }

        # 2. Запускаем проверку, где все сервисы здоровы (база восстановилась)
        with patch("alert_service.check_yandex_disk", return_value=(True, "OK", "200")):
            with patch("alert_service.check_gigachat_api", return_value=(True, "OK", "0")):
                with patch("alert_service.check_etl_worker", return_value=(True, "OK", "10s")):
                    with patch("alert_service.check_gigachat_token_balance", return_value=(True, "OK", "100%")):
                        with patch("alert_service.check_etl_performance", return_value=(True, "OK", "3.5s")):
                            with patch("alert_service.check_database_availability", return_value=(True, "База данных PostgreSQL доступна и отвечает на запросы", "Connected")):
                                with patch("alert_service.check_backup_freshness", return_value=(True, "OK", "1.0 ч")):
                                    results = run_health_checks_and_alert()

        # Должно быть отправлено 1 письмо о выздоровлении
        self.assertEqual(mock_dual_send.call_count, 1)
        args, kwargs = mock_dual_send.call_args
        subject = args[0]
        self.assertIn("ВЫЗДОРОВЛЕНИЕ", subject)
        self.assertIn("База данных PostgreSQL", subject)
        self.assertFalse(ALERT_STATES["database"]["is_active"])

    @patch("alert_service.send_dual_email")
    def test_admin_test_alert_endpoint(self, mock_dual_send):
        """Тест эндпоинта POST /api/v1/admin/alerts/test."""
        mock_dual_send.return_value = {
            "konsultantms@yandex.com": True,
            "sergo123qwe321@gmail.com": True
        }

        admin_token = create_access_token(
            {"sub": "admin_test", "role": "ADMIN", "user_id": 999}
        )

        # 1. Запрос без токена -> 401/403
        res_no_auth = self.client.post("/api/v1/admin/alerts/test")
        self.assertIn(res_no_auth.status_code, [401, 403])

        # 2. Запрос с токеном ADMIN -> 200 OK и вызов send_dual_email
        res_auth = self.client.post(
            "/api/v1/admin/alerts/test",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(res_auth.status_code, 200)
        data = res_auth.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("konsultantms@yandex.com", data["recipients"])
        self.assertIn("sergo123qwe321@gmail.com", data["recipients"])
        self.assertEqual(mock_dual_send.call_count, 1)

    def test_admin_alerts_status_endpoint(self):
        """Тест эндпоинта GET /api/v1/admin/alerts/status со всеми 7 метриками."""
        admin_token = create_access_token(
            {"sub": "admin_test", "role": "ADMIN", "user_id": 999}
        )

        res = self.client.get(
            "/api/v1/admin/alerts/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("services", data)
        self.assertIn("yandex_disk", data["services"])
        self.assertIn("gigachat_api", data["services"])
        self.assertIn("etl_worker", data["services"])
        self.assertIn("gigachat_tokens", data["services"])
        self.assertIn("etl_performance", data["services"])
        self.assertIn("database", data["services"])
        self.assertIn("backup_freshness", data["services"])
        
        backup_stat = data["services"]["backup_freshness"]
        self.assertIn("status", backup_stat)
        self.assertIn("is_active_alert", backup_stat)

    def test_check_backup_freshness_healthy(self):
        """Проверка check_backup_freshness при наличии свежего дампа (< 24ч)."""
        now = 1700000000.0
        mock_backups = [
            {
                "filename": "backup_konsyltant_20260827_010000.sql.gz",
                "filepath": "/app/backups/backup_konsyltant_20260827_010000.sql.gz",
                "size_bytes": 25000,
                "size_human": "24.4 KB",
                "mtime": now - 7200.0 # 2 часа назад
            }
        ]
        with patch("scripts.admin.backup_db.list_backups", return_value=mock_backups):
            with patch("time.time", return_value=now):
                is_healthy, desc, val = check_backup_freshness(max_age_hours=26.0)
                self.assertTrue(is_healthy)
                self.assertIn("актуален", desc)
                self.assertIn("2.0 ч", val)

    def test_check_backup_freshness_stale_and_empty(self):
        """Проверка check_backup_freshness при отсутствии файлов или устаревшем дампе (> 26ч)."""
        now = 1700000000.0
        
        # 1. Пустой каталог бэкапов
        with patch("scripts.admin.backup_db.list_backups", return_value=[]):
            is_healthy, desc, val = check_backup_freshness(max_age_hours=26.0)
            self.assertFalse(is_healthy)
            self.assertIn("отсутствуют", desc)

        # 2. Устаревший бэкап (возраст 30 часов > порога 26ч)
        stale_backups = [
            {
                "filename": "backup_konsyltant_20260825_010000.sql.gz",
                "filepath": "/app/backups/backup_konsyltant_20260825_010000.sql.gz",
                "size_bytes": 25000,
                "size_human": "24.4 KB",
                "mtime": now - (30 * 3600.0) # 30 часов назад
            }
        ]
        with patch("scripts.admin.backup_db.list_backups", return_value=stale_backups):
            with patch("time.time", return_value=now):
                is_healthy, desc, val = check_backup_freshness(max_age_hours=26.0)
                self.assertFalse(is_healthy)
                self.assertIn("устарел", desc)
                self.assertIn("30.0 ч", val)

    def test_trigger_daily_backup_if_needed(self):
        """Проверка автоматического создания бэкапа по истечении 24 часов или при их отсутствии."""
        now = 1700000000.0
        
        # 1. Дампов нет -> должен вызвать create_backup
        with patch("scripts.admin.backup_db.list_backups", return_value=[]):
            with patch("scripts.admin.backup_db.create_backup", return_value={"filename": "auto_backup.sql.gz", "size_human": "25 KB"}) as mock_create:
                res = trigger_daily_backup_if_needed(interval_hours=24.0)
                self.assertIsNotNone(res)
                self.assertEqual(mock_create.call_count, 1)

        # 2. Свежий дамп (2 часа назад) -> НЕ должен вызывать create_backup
        fresh_backups = [{"filename": "fresh.sql.gz", "mtime": now - 7200.0}]
        with patch("scripts.admin.backup_db.list_backups", return_value=fresh_backups):
            with patch("time.time", return_value=now):
                with patch("scripts.admin.backup_db.create_backup") as mock_create:
                    res = trigger_daily_backup_if_needed(interval_hours=24.0)
                    self.assertIsNone(res)
                    self.assertEqual(mock_create.call_count, 0)

        # 3. Дамп старше 24 часов (25 часов назад) -> должен вызвать create_backup
        old_backups = [{"filename": "old.sql.gz", "mtime": now - (25 * 3600.0)}]
        with patch("scripts.admin.backup_db.list_backups", return_value=old_backups):
            with patch("time.time", return_value=now):
                with patch("scripts.admin.backup_db.create_backup", return_value={"filename": "new_auto.sql.gz", "size_human": "26 KB"}) as mock_create:
                    res = trigger_daily_backup_if_needed(interval_hours=24.0)
                    self.assertIsNotNone(res)
                    self.assertEqual(mock_create.call_count, 1)


if __name__ == "__main__":
    unittest.main()
