import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", "konsultantms@yandex.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
RECIPIENT = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "konsultantms@yandex.com")

def test_smtp():
    print(f"=== ТЕСТ YANDEX SMTP ===")
    print(f"Сервер: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"Пользователь: {SMTP_USER}")
    print(f"Пароль (длина): {len(SMTP_PASSWORD)} символов")

    msg = MIMEMultipart()
    msg["Subject"] = "Тест Yandex SMTP ИИ-Консультант"
    msg["From"] = f"ИИ-Консультант <{SMTP_USER}>"
    msg["To"] = RECIPIENT
    msg.attach(MIMEText("Тестовое письмо от ИИ-Консультанта через Yandex SMTP.", "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.set_debuglevel(1)
            server.login(SMTP_USER, SMTP_PASSWORD)
            result = server.sendmail(SMTP_USER, RECIPIENT, msg.as_string())
            print(f"\n[УСПЕХ] Письмо отправлено! Результат: {result}")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n[ОШИБКА АВТОРИЗАЦИИ 535]: {e}")
        print("ВАЖНО: Пароль отклонен Яндексом. Для Yandex SMTP требуется сгенерировать 16-значный 'Пароль приложения' в Яндекс ID (Пароли приложений).")
        return False
    except Exception as e:
        print(f"\n[ОШИБКА SMTP]: {e}")
        return False

if __name__ == "__main__":
    test_smtp()
