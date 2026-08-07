import sys
from notification_service import NotificationService

def main():
    print("=== Тестирование отправки уведомлений на единый email ===")
    subject = "Тестовый доступ к ИИ-Консультанту [E2E Test]"
    body = """
    <html>
    <body>
        <h2>Тестовое уведомление системы ИИ-Консультант</h2>
        <p>Централизованная рассылка успешно перенаправлена на <b>konsultantms@yandex.com</b>.</p>
        <p><b>Ссылка для входа:</b> <a href="http://127.0.0.1:8000/?token=test_e2e_token">http://127.0.0.1:8000/?token=test_e2e_token</a></p>
        <p><b>Пароль:</b> <code>TestPass2026!</code></p>
    </body>
    </html>
    """
    success = NotificationService.send_email(subject, body, "konsultantms@yandex.com")
    print(f"Результат выполнения отправки: {success}")

if __name__ == "__main__":
    main()
