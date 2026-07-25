import os
import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from database import folder_exists, create_patient_access
from drive_api import get_drive_service

# Загружаем переменные окружения из .env
load_dotenv()

# Настройки почты
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_LOGIN = os.getenv("SMTP_LOGIN", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
TARGET_EMAIL = "sergo123qwe321@gmail.com"

# Настройки диска и проекта
ROOT_FOLDER_ID = os.getenv("ROOT_FOLDER_ID", "")
BASE_URL = "http://127.0.0.1:8000"

def generate_random_password(length=12):
    """Генерирует надежный случайный пароль"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_email(subject: str, body: str, to_email: str) -> bool:
    """Отправляет email через SMTP"""
    if not SMTP_LOGIN or not SMTP_PASSWORD:
        print("ВНИМАНИЕ: Настройки SMTP (SMTP_LOGIN, SMTP_PASSWORD) не заданы в .env.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = SMTP_LOGIN
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Ошибка при отправке Email: {e}")
        return False

def scan_folders():
    """Сканирует корневую папку и создает доступы для новых подпапок"""
    if not ROOT_FOLDER_ID:
        print("Ошибка: ROOT_FOLDER_ID не задан в .env. Невозможно просканировать корневую папку.")
        return
        
    print(f"Начинаю сканирование корневой папки: {ROOT_FOLDER_ID}")
    service = get_drive_service()
    if not service:
        print("Ошибка доступа к Google Диску.")
        return
        
    try:
        # Ищем только папки внутри корневой папки
        query = f"'{ROOT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])
        
        if not folders:
            print("В корневой папке нет подпапок обследуемых.")
            return
            
        new_count = 0
        for folder in folders:
            folder_id = folder['id']
            folder_name = folder['name']
            
            # Проверяем, зарегистрирована ли папка в SQLite
            if not folder_exists(folder_id):
                print(f"Обнаружена новая папка: {folder_name} (ID: {folder_id})")
                
                # Генерируем пароль и сохраняем доступ в БД
                password = generate_random_password()
                access_token = create_patient_access(password, folder_id)
                
                # Формируем ссылку и письмо
                login_link = f"{BASE_URL}/?token={access_token}"
                
                subject = f"Доступ к ИИ-Консультанту: Пациент {folder_name}"
                body = f"""
                <html>
                <body>
                    <h2>Здравствуйте!</h2>
                    <p>Для новой папки обследуемого <b>{folder_name}</b> успешно сгенерирован защищенный доступ.</p>
                    <p><b>Ссылка для входа:</b> <a href="{login_link}">{login_link}</a></p>
                    <p><b>Пароль:</b> <code>{password}</code></p>
                    <br>
                    <p><i>С уважением,<br>Система ИИ-Консультант</i></p>
                </body>
                </html>
                """
                
                print(f"Отправка Email для {folder_name}...")
                if send_email(subject, body, TARGET_EMAIL):
                    print(f"[+] Доступ для '{folder_name}' отправлен на {TARGET_EMAIL}")
                else:
                    print(f"[-] Доступ для '{folder_name}' создан в БД, но письмо отправить не удалось.")
                    
                new_count += 1
                
        if new_count == 0:
            print("Сканирование завершено. Все папки уже зарегистрированы в системе.")
        else:
            print(f"Успешно обработано новых папок: {new_count}")

    except Exception as e:
        print(f"Ошибка при поиске папок на Google Диске: {e}")

if __name__ == "__main__":
    scan_folders()
