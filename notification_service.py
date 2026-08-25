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
    def send_welcome_email(
        recipient_email: str, 
        access_token: str, 
        passcode: str, 
        folder_name: str, 
        base_url: str = None, 
        folder_public_url: str = None,
        cache_public_url: str = None
    ) -> bool:
        if not base_url or ":8000" in base_url:
            base_url = os.getenv("BASE_URL", "https://xn--g1aj3a.site")
            if ":8000" in base_url:
                base_url = "https://xn--g1aj3a.site"
        base_url = base_url.rstrip("/")
        login_link = f"{base_url}/app/?token={access_token}"
        
        # БЕЗОПАСНОЕ ЛОГИРОВАНИЕ (CWE-532 REDACTION)
        masked_link = mask_url(login_link)
        masked_pass = mask_credential(passcode)
        masked_folder_url = mask_url(folder_public_url) if folder_public_url else "N/A"
        masked_cache_url = mask_url(cache_public_url) if cache_public_url else "N/A"
        print(f"[SECURE LOG] Подготовка отправки доступов для '{folder_name}' | URL: {masked_link} | Passcode: {masked_pass} | Folder Public URL: {masked_folder_url} | Cache Public URL: {masked_cache_url}")

        subject = f"Доступ к ИИ-Консультанту: Пациент {folder_name}"
        
        folder_link_html = f'<p><b>Ссылка на папку на Яндекс.Диске:</b> <a href="{folder_public_url}">{folder_public_url}</a></p>' if folder_public_url else ''
        if cache_public_url:
            cache_link_html = f'<p><b>Ссылка на кэш-файл:</b> <a href="{cache_public_url}">{cache_public_url}</a></p>'
        else:
            cache_link_html = '<p><b>Ссылка на кэш-файл:</b> Ссылка на кэш-файл будет сформирована после обработки</p>'

        body = f"""
        <html>
        <body>
            <h2>Здравствуйте!</h2>
            <p>Для новой папки обследуемого <b>{folder_name}</b> успешно сгенерирован защищенный доступ.</p>
            <p><b>Ссылка для входа:</b> <a href="{login_link}">{login_link}</a></p>
            <p><b>Пароль:</b> <code>{passcode}</code></p>
            {folder_link_html}
            {cache_link_html}
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

def send_email_to_recipient(email: str, subject: str, html_body: str) -> bool:
    """Удобная функция отправки HTML-письма на указанный адрес."""
    return NotificationService.send_smtp_email(subject, html_body, email)

def send_doctor_onboarding_email(doctor_email: str, full_name: str, temp_password: str, specialty: str) -> bool:
    """
    Отправляет реквизиты доступа новому врачу/специалисту с дублированием на корпоративный адрес центра.
    """
    base_url = os.getenv("BASE_URL", "https://xn--g1aj3a.site").rstrip("/")
    if ":8000" in base_url:
        base_url = "https://xn--g1aj3a.site"
        
    login_url = f"{base_url}/#doctor"
    masked_email = mask_credential(doctor_email)
    masked_pass = mask_credential(temp_password)
    print(f"[ONBOARDING DOCTOR] Подготовка отправки доступов для врача '{full_name}' | Email: {masked_email} | Pass: {masked_pass}")

    subject = "Доступ к кабинету врача — Центр «Маленькая Страна»"
    
    html_body = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0F172A; color: #F8FAFC; margin: 0; padding: 24px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #1E293B; border-radius: 16px; border: 1px solid #7C3AED; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            .header {{ background: linear-gradient(135deg, #7C3AED, #06B6D4); padding: 24px; text-align: center; color: #ffffff; }}
            .header h1 {{ margin: 0; font-size: 20px; font-weight: 700; }}
            .header p {{ margin: 6px 0 0 0; font-size: 13px; opacity: 0.9; }}
            .content {{ padding: 24px; }}
            .badge {{ display: inline-block; background: rgba(124, 58, 237, 0.2); color: #C084FC; border: 1px solid #7C3AED; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-bottom: 16px; }}
            .card {{ background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 18px; margin: 18px 0; }}
            .cred-row {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; }}
            .cred-label {{ color: #94A3B8; font-weight: 500; }}
            .cred-value {{ color: #F8FAFC; font-weight: 600; font-family: monospace; background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 4px; }}
            .btn {{ display: block; text-align: center; background: #7C3AED; color: #ffffff !important; text-decoration: none; padding: 14px 20px; border-radius: 8px; font-weight: 600; font-size: 15px; margin: 20px 0; }}
            .alert-box {{ background: rgba(239, 68, 68, 0.1); border-left: 4px solid #EF4444; padding: 12px 14px; border-radius: 4px; font-size: 12px; color: #FCA5A5; line-height: 1.5; margin-top: 20px; }}
            .footer {{ padding: 16px 24px; text-align: center; font-size: 12px; color: #64748B; border-top: 1px solid rgba(255,255,255,0.06); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Центр ментального здоровья «Маленькая Страна»</h1>
                <p>Единая цифровая диагностическая платформа</p>
            </div>
            <div class="content">
                <span class="badge">🩺 Кабинет специалиста</span>
                <h2 style="margin: 0 0 10px 0; font-size: 18px; color: #F8FAFC;">Здравствуйте, {full_name}!</h2>
                <p style="font-size: 14px; line-height: 1.5; color: #CBD5E1; margin: 0 0 16px 0;">
                    Для вас создана учетная запись врача в центре ментального здоровья детей «Маленькая Страна».
                    Специализация: <strong>{specialty}</strong>.
                </p>
                
                <div class="card">
                    <div style="font-size: 13px; font-weight: 600; color: #A78BFA; margin-bottom: 12px;">🔑 ВАШИ РЕКВИЗИТЫ ДЛЯ ВХОДА:</div>
                    <div style="margin-bottom: 8px;">
                        <span style="color: #94A3B8; font-size: 13px;">Логин (Email):</span><br>
                        <strong style="color: #38BDF8; font-size: 15px;">{doctor_email}</strong>
                    </div>
                    <div>
                        <span style="color: #94A3B8; font-size: 13px;">Временный пароль:</span><br>
                        <code style="display: inline-block; margin-top: 4px; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.15); color: #4ADE80; font-size: 16px; padding: 4px 10px; border-radius: 6px; letter-spacing: 1px;">{temp_password}</code>
                    </div>
                </div>

                <a href="{login_url}" class="btn" style="color: #ffffff;">Войти в кабинет врача 🩺</a>

                <div class="alert-box">
                    <strong>🛡️ БЕЗОПАСНОСТЬ И ВРАЧЕБНАЯ ТАЙНА (152-ФЗ):</strong><br>
                    • Рекомендуем сменить временный пароль при первом входе.<br>
                    • Доступ к медицинским документам и картам детей строго конфиденциален.<br>
                    • Передача учетных данных третьим лицам категорически запрещена.
                </div>
            </div>
            <div class="footer">
                © Центр ментального здоровья детей «Маленькая Страна» | Домен: цмз.site<br>
                По техническим вопросам: konsultantms@yandex.com
            </div>
        </div>
    </body>
    </html>
    """

    try:
        # Отправка на почту врача
        success_doc = send_email_to_recipient(doctor_email, subject, html_body)
        
        # Обязательное дублирование на корпоративный адрес клиники
        primary_alert = os.getenv("PRIMARY_ALERT_EMAIL", "konsultantms@yandex.com")
        if primary_alert and primary_alert != doctor_email:
            send_email_to_recipient(primary_alert, f"[КОПИЯ ОНБОРДИНГА] {subject} ({full_name})", html_body)
            
        return success_doc
    except Exception as e:
        print(f"[ONBOARDING DOCTOR ERROR] Сбой отправки письма врачу {doctor_email}: {e}")
        return False

def send_dual_email(subject: str, html_body: str, primary_email: str = None, secondary_email: str = None) -> dict:
    """Отправляет письмо с дублированием на два ключевых адреса."""
    p_email = primary_email or os.getenv("PRIMARY_ALERT_EMAIL", "konsultantms@yandex.com")
    s_email = secondary_email or os.getenv("SECONDARY_ALERT_EMAIL", "sergo123qwe321@gmail.com")
    
    res_p = send_email_to_recipient(p_email, subject, html_body)
    res_s = send_email_to_recipient(s_email, subject, html_body) if s_email else False
    
    return {
        p_email: res_p,
        s_email: res_s,
        "success": res_p or res_s
    }

