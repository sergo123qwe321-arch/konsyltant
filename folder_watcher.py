import os
import smtplib
import socket
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
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_LOGIN = os.getenv("SMTP_LOGIN", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
TARGET_EMAIL = "sergo123qwe321@gmail.com"

# Настройки диска и проекта
ROOT_FOLDER_ID = os.getenv("ROOT_FOLDER_ID", "")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def generate_random_password(length=12):
    """Генерирует надежный случайный пароль"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_email(subject: str, body: str, to_email: str) -> bool:
    """Отправляет email через SMTP"""
    if not SMTP_LOGIN or not SMTP_PASSWORD:
        print("[FOLDER WATCHER ERROR] ВНИМАНИЕ: Настройки SMTP (SMTP_LOGIN, SMTP_PASSWORD) не заданы.")
        return False
        
    msg = MIMEMultipart()
    msg['From'] = SMTP_LOGIN
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    print(f"[FOLDER WATCHER] Попытка отправки с {SMTP_LOGIN} через {SMTP_SERVER}:{SMTP_PORT} на {to_email}...")
    try:
        # Принудительно заставляем сокет использовать только IPv4 (AF_INET),
        # чтобы избежать ошибки "Network is unreachable" (IPv6) на серверах Render.
        _orig_getaddrinfo = socket.getaddrinfo
        def force_ipv4(host, port, family=0, type=0, proto=0, flags=0):
            return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        
        socket.getaddrinfo = force_ipv4
        
        try:
            # Используем SMTP_SSL (порт 465) с таймаутом 15с через контекстный менеджер
            with smtplib.SMTP_SSL(SMTP_SERVER, 465, timeout=15) as server:
                server.login(SMTP_LOGIN, SMTP_PASSWORD)
                server.send_message(msg)
        finally:
            # Возвращаем стандартное поведение getaddrinfo
            socket.getaddrinfo = _orig_getaddrinfo
            
        print(f"[FOLDER WATCHER SUCCESS] Письмо успешно отправлено на {to_email}!")
        return True
    except socket.timeout:
        print(f"[FOLDER WATCHER ERROR] Таймаут подключения к Gmail SMTP (15 сек).")
        return False
    except smtplib.SMTPException as e:
        print(f"[FOLDER WATCHER ERROR] Ошибка SMTP при отправке на {to_email}: {e}")
        return False
    except Exception as e:
        print(f"[FOLDER WATCHER ERROR] Сбой отправки Email на {to_email}: {e}")
        return False

def scan_folders():
    """Сканирует все доступные папки и создает доступы для новых подпапок"""
    print(f"\n[FOLDER WATCHER] Старт цикла проверки. ROOT_FOLDER_ID: {ROOT_FOLDER_ID}")
    
    if not ROOT_FOLDER_ID:
        print("[FOLDER WATCHER ERROR] ROOT_FOLDER_ID не задан в .env. Невозможно просканировать папки.")
        return
        
    try:
        service = get_drive_service()
        if not service:
            print("[FOLDER WATCHER ERROR] Ошибка доступа к Google Диску (сервис не инициализирован).")
            return
            
        # Убираем ограничение in parents, чтобы находить папки на любой глубине вложенности
        query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])
        
        if not folders:
            print("[FOLDER WATCHER] Доступные папки не найдены (возможно, нет доступа).")
            return
            
        new_count = 0
        for folder in folders:
            folder_id = folder['id']
            folder_name = folder['name']
            
            # Игнорируем саму корневую папку
            if folder_id == ROOT_FOLDER_ID:
                continue
                
            print(f"[FOLDER WATCHER] Проверка папки: '{folder_name}' (ID: {folder_id})")
            
            # Проверяем, зарегистрирована ли папка в SQLite
            if not folder_exists(folder_id):
                print(f"[FOLDER WATCHER] [+] Обнаружена новая папка: {folder_name}")
                
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
                
                print(f"[FOLDER WATCHER] Отправка Email для {folder_name}...")
                if send_email(subject, body, TARGET_EMAIL):
                    print(f"[FOLDER WATCHER] [OK] Доступ для '{folder_name}' отправлен на {TARGET_EMAIL}")
                else:
                    print(f"[FOLDER WATCHER ERROR] Доступ для '{folder_name}' создан в БД, но письмо отправить не удалось.")
                    
                new_count += 1
                
        if new_count == 0:
            print("[FOLDER WATCHER] Новых папок нет.")
        else:
            print(f"[FOLDER WATCHER] Успешно обработано новых папок: {new_count}")

    except Exception as e:
        print(f"[FOLDER WATCHER ERROR] Критическая ошибка API Google Drive: {e}")

if __name__ == "__main__":
    scan_folders()
