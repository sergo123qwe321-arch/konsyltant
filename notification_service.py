import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
from dotenv import load_dotenv
from security_utils import mask_credential, mask_url

load_dotenv()

logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER", os.getenv("YANDEX_EMAIL", "konsultantms@yandex.com"))
DEFAULT_NOTIFICATION_EMAIL = os.getenv("DEFAULT_NOTIFICATION_EMAIL", "konsultantms@yandex.com")
UNISENDER_API_KEY = os.getenv("UNISENDER_API_KEY", "")

class NotificationService:
    @staticmethod
    def send_smtp_email(subject: str, body: str, recipient_email: str = None) -> bool:
        """
        Отправляет email через Yandex SMTP (SSL порт 465).
        """
        smtp_pass = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
        target_email = recipient_email or DEFAULT_NOTIFICATION_EMAIL

        print(f"[NOTIFICATION SERVICE] SMTP Password status: loaded (length: {len(smtp_pass)})")
        print(f"[NOTIFICATION SERVICE] Отправка через Yandex SMTP ({SMTP_SERVER}:{SMTP_PORT}) на {target_email}...")

        if not smtp_pass:
            print("[NOTIFICATION SERVICE WARNING] SMTP_PASSWORD не задан в .env.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_USER
            msg["To"] = target_email
            msg.attach(MIMEText(body, "html", "utf-8"))

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
                server.set_debuglevel(0)  # Безопасное логирование без вывода сырых данных аутентификации
                server.login(SMTP_USER, smtp_pass)
                server.sendmail(SMTP_USER, target_email, msg.as_string())

            print(f"[NOTIFICATION SERVICE SUCCESS] [250 OK] Письмо успешно отправлено через Yandex SMTP на {target_email}!")
            return True
        except Exception as e:
            print(f"[NOTIFICATION SERVICE ERROR] Сбой отправки Yandex SMTP: {e}")
            return False

    @staticmethod
    def send_unisender_email(subject: str, body: str, recipient_email: str = None) -> bool:
        target_email = recipient_email or DEFAULT_NOTIFICATION_EMAIL
        if not UNISENDER_API_KEY:
            return False

        url = "https://api.unisender.com/ru/api/sendEmail"
        params = {
            "format": "json",
            "api_key": UNISENDER_API_KEY,
            "email": target_email,
            "sender_name": "ИИ-Консультант",
            "sender_email": SMTP_USER,
            "subject": subject,
            "body": body,
            "list_id": 1
        }
        try:
            res = requests.post(url, data=params, timeout=15)
            print(f"[UNISENDER API LOG] Status: {res.status_code}")
            return res.status_code == 200 and "result" in res.json()
        except Exception as e:
            print(f"[UNISENDER ERROR]: {e}")
            return False

    @staticmethod
    def send_welcome_email(recipient_email: str, access_token: str, passcode: str, folder_name: str, base_url: str = "http://127.0.0.1:8000", folder_public_url: str = None) -> bool:
        login_link = f"{base_url}/?token={access_token}"
        
        # БЕЗОПАСНОЕ ЛОГИРОВАНИЕ (CWE-532 REDACTION)
        masked_link = mask_url(login_link)
        masked_pass = mask_credential(passcode)
        masked_folder_url = mask_url(folder_public_url) if folder_public_url else "N/A"
        print(f"[SECURE LOG] Подготовка отправки доступов для '{folder_name}' | URL: {masked_link} | Passcode: {masked_pass} | Folder Public URL: {masked_folder_url}")

        subject = f"Доступ к ИИ-Консультанту: Пациент {folder_name}"
        
        folder_link_html = f'<p><b>Ссылка на папку на Яндекс.Диске:</b> <a href="{folder_public_url}">{folder_public_url}</a></p>' if folder_public_url else ''
        cache_placeholder_html = '<p><b>Ссылка на кэш-файл:</b> Ссылка на кэш-файл будет сформирована после обработки</p>'

        body = f"""
        <html>
        <body>
            <h2>Здравствуйте!</h2>
            <p>Для новой папки обследуемого <b>{folder_name}</b> успешно сгенерирован защищенный доступ.</p>
            <p><b>Ссылка для входа:</b> <a href="{login_link}">{login_link}</a></p>
            <p><b>Пароль:</b> <code>{passcode}</code></p>
            {folder_link_html}
            {cache_placeholder_html}
            <br>
            <p><i>С уважением,<br>Система ИИ-Консультант</i></p>
        </body>
        </html>
        """

        success = NotificationService.send_smtp_email(subject, body, recipient_email)
        if not success:
            print("[NOTIFICATION SERVICE] Пробуем резервный Unisender API...")
            success = NotificationService.send_unisender_email(subject, body, recipient_email)

        return success
