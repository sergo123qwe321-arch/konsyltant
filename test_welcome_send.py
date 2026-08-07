from notification_service import NotificationService
from security_utils import mask_credential

def main():
    print("=== Е2Е ТЕСТ ОТПРАВКИ EMAIL УВЕДОМЛЕНИЯ ПАВЛИКА МОРОЗОВА ===")
    test_token = "ue3E6fFU14JJAL1GemgpkmOr9zA0wqUcPcPcr4-qLus"
    test_pass = "hsDCORkIlZ1Y"
    print(f"[TEST LOG] Отправка теста для токена {mask_credential(test_token)} | Pass: {mask_credential(test_pass)}")
    
    sent = NotificationService.send_welcome_email(
        recipient_email="konsultantms@yandex.com",
        access_token=test_token,
        passcode=test_pass,
        folder_name="Павлик Морозов"
    )
    print(f"\nИтоговый результат функции send_welcome_email: {sent}")

if __name__ == "__main__":
    main()
