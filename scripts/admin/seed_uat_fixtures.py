import os
import sys
import json
import bcrypt
from dotenv import load_dotenv

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()

from database import init_db, get_connection, execute_query, check_is_postgres
from scripts.admin.seed_production_posts import seed_production_posts

def seed_uat_fixtures():
    print("=" * 70)
    print("🚀 СИДИРОВАНИЕ ЕДИНОГО НАБОРА UAT-ДАННЫХ (DOCTOR, PATIENT, ADMIN, POSTS)")
    print("=" * 70)

    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    is_postgres = check_is_postgres()
    bool_true = True if is_postgres else 1

    # 1. ВРАЧ (DOCTOR)
    doc_email = "producer@cmz.site"
    doc_pass = "TestAccess2026!"
    doc_name = "Доктор Продюсер"
    doc_spec = "Главный Продюсер / Клинический Эксперт"
    doc_license = "DOC-PRODUCER"
    doc_salt = bcrypt.gensalt()
    doc_hash = bcrypt.hashpw(doc_pass.encode('utf-8'), doc_salt).decode('utf-8')

    execute_query(cursor, "SELECT id FROM doctors WHERE email = ?", (doc_email,))
    doc_row = cursor.fetchone()
    if doc_row:
        execute_query(cursor, """
            UPDATE doctors
            SET full_name = ?, specialty = ?, password_hash = ?, license_number = ?, is_verified = ?
            WHERE id = ?
        """, (doc_name, doc_spec, doc_hash, doc_license, bool_true, doc_row[0]))
        print(f"✅ Врач '{doc_email}' обновлен в таблице doctors (ID: {doc_row[0]}).")
    else:
        execute_query(cursor, """
            INSERT INTO doctors (email, full_name, specialty, password_hash, license_number, is_verified, role)
            VALUES (?, ?, ?, ?, ?, ?, 'DOCTOR')
        """, (doc_email, doc_name, doc_spec, doc_hash, doc_license, bool_true))
        print(f"✅ Врач '{doc_email}' создан в таблице doctors.")

    # Дублируем/гарантируем в patient_access для единого входа
    execute_query(cursor, "SELECT id FROM patient_access WHERE access_token = ? OR email = ?", (doc_email, doc_email))
    pa_doc = cursor.fetchone()
    if pa_doc:
        execute_query(cursor, """
            UPDATE patient_access
            SET password_hash = ?, full_name = ?, specialization = ?, role = 'DOCTOR', is_verified = ?, email = ?
            WHERE id = ?
        """, (doc_hash, doc_name, doc_spec, bool_true, doc_email, pa_doc[0]))
    else:
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, full_name, specialization, role, is_verified, email)
            VALUES (?, ?, 'doctor_vault_producer', ?, ?, 'DOCTOR', ?, ?)
        """, (doc_email, doc_hash, doc_name, doc_spec, bool_true, doc_email))

    # 2. ПАЦИЕНТ (PATIENT)
    pat_token = "test_patient_token_2026"
    pat_email = "patient@cmz.site"
    pat_pass = "PatientAccess2026!"
    pat_folder = "disk:/Тестовый Пациент"
    pat_name = "Тестовый Пациент"
    pat_salt = bcrypt.gensalt()
    pat_hash = bcrypt.hashpw(pat_pass.encode('utf-8'), pat_salt).decode('utf-8')

    execute_query(cursor, "SELECT id FROM patient_access WHERE access_token = ? OR email = ?", (pat_token, pat_email))
    pat_row = cursor.fetchone()
    if pat_row:
        execute_query(cursor, """
            UPDATE patient_access
            SET access_token = ?, email = ?, password_hash = ?, gdrive_folder_id = ?, full_name = ?, role = 'PATIENT', is_verified = ?
            WHERE id = ?
        """, (pat_token, pat_email, pat_hash, pat_folder, pat_name, bool_true, pat_row[0]))
        print(f"✅ Пациент '{pat_token}' ({pat_email}) обновлен в patient_access (ID: {pat_row[0]}).")
    else:
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, email, password_hash, gdrive_folder_id, full_name, role, is_verified)
            VALUES (?, ?, ?, ?, ?, 'PATIENT', ?)
        """, (pat_token, pat_email, pat_hash, pat_folder, pat_name, bool_true))
        print(f"✅ Пациент '{pat_token}' ({pat_email}) создан в patient_access.")

    # 3. АДМИНИСТРАТОР (ADMIN)
    admin_login = "producer-admin@cmz.site"
    admin_pass = "AdminAccess2026!"
    admin_name = "Продюсер Администратор"
    admin_spec = "Главный администратор CMS"
    admin_salt = bcrypt.gensalt()
    admin_hash = bcrypt.hashpw(admin_pass.encode('utf-8'), admin_salt).decode('utf-8')

    execute_query(cursor, "SELECT id FROM patient_access WHERE access_token = ?", (admin_login,))
    admin_row = cursor.fetchone()
    if admin_row:
        execute_query(cursor, """
            UPDATE patient_access
            SET password_hash = ?, full_name = ?, specialization = ?, role = 'ADMIN', is_verified = ?, email = ?
            WHERE id = ?
        """, (admin_hash, admin_name, admin_spec, bool_true, admin_login, admin_row[0]))
        print(f"✅ Администратор '{admin_login}' обновлен в patient_access (ID: {admin_row[0]}).")
    else:
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, email, password_hash, gdrive_folder_id, full_name, specialization, role, is_verified)
            VALUES (?, ?, ?, 'admin_vault_producer', ?, ?, 'ADMIN', ?)
        """, (admin_login, admin_login, admin_hash, admin_name, admin_spec, bool_true))
        print(f"✅ Администратор '{admin_login}' создан в patient_access.")

    conn.commit()
    conn.close()

    # 4. ПОСТЫ ЭКСПЕРТНОГО БЛОГА
    seed_production_posts()

    print("=" * 70)
    print("📋 РЕКВИЗИТЫ ДОСТУПА ДЛЯ UAT-ТЕСТИРОВАНИЯ:")
    print(f"🩺 Врач:          {doc_email} / {doc_pass}")
    print(f"🧸 Пациент (токен): {pat_token} / {pat_pass}")
    print(f"🧸 Пациент (email): {pat_email} / {pat_pass}")
    print(f"👑 Администратор: {admin_login} / {admin_pass}")
    print("=" * 70)

if __name__ == "__main__":
    seed_uat_fixtures()
