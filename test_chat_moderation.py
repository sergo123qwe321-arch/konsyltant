import unittest
import uuid
from security_utils import contains_profanity, process_chat_message_moderation
from database import (
    init_db, create_public_chat_message, get_public_chat_messages,
    get_unapproved_chat_messages, approve_public_chat_message,
    ban_user, is_user_banned, create_chat_report, get_message_reports_count
)

class TestChatModeration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_profanity_filter(self):
        clean_samples = [
            "Здравствуйте! Подскажите, как записаться на прием к неврологу?",
            "Ребенку 4 года, плохо говорит буквы Р и Л",
            "Спасибо специалистам за замечательное занятие!",
            "Уточните стоимость консультации психолога"
        ]
        for text in clean_samples:
            self.assertFalse(contains_profanity(text), f"Clean text falsely flagged: {text}")

        profane_samples = [
            "Это блять какой-то ужас",
            "Пошел на хуй отсюда",
            "Ну ты и сука конченая",
            "Какого хуя нет ответа",
            "Вы все тут пидоры и мудаки"
        ]
        for text in profane_samples:
            self.assertTrue(contains_profanity(text), f"Profane text not caught: {text}")

    def test_process_chat_message_moderation_profanity(self):
        with self.assertRaises(ValueError) as ctx:
            process_chat_message_moderation("Привет, это блять недопустимо")
        self.assertIn("недопустимую лексику", str(ctx.exception))

    def test_process_chat_message_moderation_shorteners(self):
        with self.assertRaises(ValueError) as ctx:
            process_chat_message_moderation("Смотрите по ссылке: https://bit.ly/secret123")
        self.assertIn("сокращенных ссылок", str(ctx.exception))

    def test_process_chat_message_moderation_allowlist_url(self):
        text = "Вот полезное видео от логопеда: https://rutube.ru/video/123456/ и фото https://images.yandex.ru/pic.png"
        processed, is_approved = process_chat_message_moderation(text)
        self.assertTrue(is_approved)
        self.assertIn("rutube.ru", processed)
        self.assertIn("images.yandex.ru", processed)

    def test_process_chat_message_moderation_unknown_url_queued(self):
        text = "Перейдите на наш сторонний форум https://unknown-suspicious-portal.org/chat для обсуждения"
        processed, is_approved = process_chat_message_moderation(text)
        self.assertFalse(is_approved)
        self.assertIn("[ссылка ожидает проверки модератором]", processed)
        self.assertNotIn("unknown-suspicious-portal.org", processed)

    def test_db_ban_and_check(self):
        uid = f"violator_{uuid.uuid4().hex[:6]}"
        role = "PATIENT"
        
        # Before ban
        banned, reason, until = is_user_banned(uid, role)
        self.assertFalse(banned)

        # Apply 24h ban
        ban_res = ban_user(uid, role, reason="Спам сторонними ссылками", duration_hours=24)
        self.assertEqual(ban_res["user_id"], uid)

        # After ban
        banned, reason, until = is_user_banned(uid, role)
        self.assertTrue(banned)
        self.assertIn("Спам", reason)

    def test_db_reports_and_autoban(self):
        author_id = f"spammer_{uuid.uuid4().hex[:6]}"
        msg = create_public_chat_message("PATIENT", author_id, "Спамер", "Купите таблетки на сайте", is_approved=True)
        msg_id = msg["id"]

        rep_prefix = uuid.uuid4().hex[:4]
        # Report 1
        r1 = create_chat_report(msg_id, f"u1_{rep_prefix}", "PATIENT", "Спам")
        self.assertEqual(r1["report_count"], 1)
        self.assertFalse(r1["is_banned"])

        # Report 2
        r2 = create_chat_report(msg_id, f"u2_{rep_prefix}", "PATIENT", "Спам")
        self.assertEqual(r2["report_count"], 2)
        self.assertFalse(r2["is_banned"])

        # Report 3 -> Auto-ban
        r3 = create_chat_report(msg_id, f"u3_{rep_prefix}", "DOCTOR", "Спам реклама")
        self.assertEqual(r3["report_count"], 3)
        self.assertTrue(r3["is_banned"])

        # Author should now be banned
        banned, reason, _ = is_user_banned(author_id, "PATIENT")
        self.assertTrue(banned)

    def test_moderation_queue_and_approve(self):
        msg = create_public_chat_message("PATIENT", f"user_{uuid.uuid4().hex[:6]}", "Мама", "Посмотрите [ссылка ожидает проверки модератором]", is_approved=False)
        msg_id = msg["id"]

        unapproved = get_unapproved_chat_messages()
        unapproved_ids = [m["id"] for m in unapproved]
        self.assertIn(msg_id, unapproved_ids)

        approve_public_chat_message(msg_id)

        unapproved_after = get_unapproved_chat_messages()
        unapproved_ids_after = [m["id"] for m in unapproved_after]
        self.assertNotIn(msg_id, unapproved_ids_after)

if __name__ == "__main__":
    unittest.main()
