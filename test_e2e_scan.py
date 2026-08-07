import os
import sys
from dotenv import load_dotenv

load_dotenv()

from notification_service import NotificationService
from folder_watcher import scan_folders
from security_utils import mask_credential

def main():
    print("=== E2E Тестирование Yandex SMTP и генерации доступа ===")
    
    test_folder = "Тестовый Пациент Иванов И.И."
    test_token = "e2e_yandex_smtp_test_token_2026"
    test_pass = "SecurePass123!"
    
    print(f"\n--- Вызов NotificationService.send_welcome_email (Token: {mask_credential(test_token)}) ---")
    sent = NotificationService.send_welcome_email(
        recipient_email="konsultantms@yandex.com",
        access_token=test_token,
        passcode=test_pass,
        folder_name=test_folder
    )
    print(f"Статус отправки Yandex SMTP: {sent}")
    
    print("\n--- Запуск scan_folders() ---")
    scan_folders()

if __name__ == "__main__":
    main()
