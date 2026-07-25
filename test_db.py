from database import init_db, create_patient_access, verify_access

def main():
    print("Инициализация базы данных SQLite...")
    init_db()
    
    print("Создание тестового доступа...")
    password = "SuperSecretPassword123"
    test_folder_id = "1Hs5A-kx0WfoR8vhUX5xX_XqMtVcwgHu6" 
    
    token = create_patient_access(password, test_folder_id)
    print(f"Доступ успешно создан!")
    print(f"Секретный токен для ссылки: {token}")
    print(f"Оригинальный пароль: {password}")
    
    print("\n[ТЕСТ 1] Проверка авторизации с правильным паролем...")
    folder_id = verify_access(token, password)
    if folder_id:
        print(f"[+] УСПЕХ: Пароль верен. ID папки получен: {folder_id}")
    else:
        print("[-] ОШИБКА: Авторизация провалилась.")
        
    print("\n[ТЕСТ 2] Проверка авторизации с неверным паролем...")
    folder_id_wrong = verify_access(token, "WrongPassword")
    if folder_id_wrong:
        print(f"[-] ОШИБКА: Авторизация прошла с неверным паролем!")
    else:
        print("[+] УСПЕХ: Неверный пароль был отклонен.")

if __name__ == "__main__":
    main()
