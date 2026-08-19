import sys
import os
import bcrypt

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import get_connection, execute_query, DATABASE_URL, psycopg2, init_db

def seed_producer():
    """
    Идемпотентный скрипт создания тестовой учетной записи врача для Продюсера.
    Создает/обновляет запись в `doctors` и `patient_access`.
    """
    print("=== ИНИЦИАЛИЗАЦИЯ ТЕСТОВОГО ДОСТУПА ПРОДЮСЕРА ===")
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    is_postgres = bool(DATABASE_URL and psycopg2)
    val_verified = True if is_postgres else 1

    full_name = "Тестовый Продюсер"
    license_number = "PRODUCER-001"
    specialty = "Главный Продюсер / Клинический Эксперт"
    email = "producer@cmz.site"
    raw_password = "TestAccess2026!"
    
    # 1. Хэширование пароля
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    # 2. Создание/Обновление в таблице doctors
    execute_query(cursor, "SELECT id FROM doctors WHERE license_number = ? OR email = ? OR full_name = ?", (license_number, email, full_name))
    doc_row = cursor.fetchone()
    if doc_row:
        doc_id = doc_row[0]
        execute_query(cursor, """
            UPDATE doctors 
            SET full_name = ?, specialty = ?, license_number = ?, is_verified = ?, email = ?, password_hash = ?, role = 'DOCTOR'
            WHERE id = ?
        """, (full_name, specialty, license_number, val_verified, email, password_hash, doc_id))
        print(f"[DOCTORS] Профиль врача #{doc_id} ('{full_name}') успешно обновлен.")
    else:
        execute_query(cursor, """
            INSERT INTO doctors (full_name, specialty, license_number, is_verified, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?, 'DOCTOR')
        """, (full_name, specialty, license_number, val_verified, email, password_hash))
        print(f"[DOCTORS] Создан новый профиль врача '{full_name}' ({license_number}).")

    # 3. Создание/Обновление в таблице patient_access (для авторизации по email/токену)
    execute_query(cursor, "SELECT id FROM patient_access WHERE access_token = ?", (email,))
    acc_row = cursor.fetchone()
    if acc_row:
        acc_id = acc_row[0]
        execute_query(cursor, """
            UPDATE patient_access
            SET password_hash = ?, role = 'DOCTOR', is_verified = ?, full_name = ?, specialization = ?
            WHERE id = ?
        """, (password_hash, val_verified, full_name, specialty, acc_id))
        print(f"[AUTH] Учетная запись авторизации #{acc_id} ('{email}') успешно обновлена.")
    else:
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, is_verified, full_name, specialization, experience_years)
            VALUES (?, ?, 'producer_vault', 'DOCTOR', ?, ?, ?, 15)
        """, (email, password_hash, val_verified, full_name, specialty))
        print(f"[AUTH] Создана новая учетная запись авторизации '{email}'.")

    # Также регистрируем номер лицензии как альтернативный логин
    execute_query(cursor, "SELECT id FROM patient_access WHERE access_token = ?", (license_number,))
    lic_row = cursor.fetchone()
    if lic_row:
        execute_query(cursor, """
            UPDATE patient_access
            SET password_hash = ?, role = 'DOCTOR', is_verified = ?, full_name = ?, specialization = ?
            WHERE id = ?
        """, (password_hash, val_verified, full_name, specialty, lic_row[0]))
    else:
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, is_verified, full_name, specialization, experience_years)
            VALUES (?, ?, 'producer_vault', 'DOCTOR', ?, ?, ?, 15)
        """, (license_number, password_hash, val_verified, full_name, specialty))

    conn.commit()
    conn.close()

    print("\n" + "="*65)
    print("✅ ТЕСТОВЫЙ ДОСТУП ДЛЯ ПРОДЮСЕРА УСПЕШНО ГОТОВ К РАБОТЕ!")
    print("="*65)
    print(f"📌 Портал:           https://цмз.site  (или http://159.194.232.74)")
    print(f"🩺 Раздел входа:     «Кабинет врача» (кнопка в подвале или #doctor)")
    print(f"👤 Логин / Email:    {email}  (или {license_number})")
    print(f"🔑 Пароль:           {raw_password}")
    print(f"🏷️ Роль / Статус:    DOCTOR (Верифицированный специалист)")
    print(f"👨‍⚕️ ФИО:              {full_name}")
    print(f"📜 Номер лицензии:   {license_number}")
    print("="*65 + "\n")

if __name__ == '__main__':
    seed_producer()
