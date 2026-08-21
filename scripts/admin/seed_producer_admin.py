import os
import sys
import bcrypt
from dotenv import load_dotenv

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()

from database import init_db, get_connection, execute_query

def seed_producer_admin():
    init_db()
    
    admin_login = "producer-admin@cmz.site"
    admin_pass = "AdminAccess2026!"
    role = "ADMIN"
    vault_folder_id = "admin_vault_producer"
    full_name = "Продюсер Администратор"
    specialization = "Главный администратор CMS"
    experience_years = 10
    
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(admin_pass.encode('utf-8'), salt).decode('utf-8')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🚀 СИДИРОВАНИЕ УЧЁТНОЙ ЗАПИСИ АДМИНИСТРАТОРА (ПРОДЮСЕР)")
    print("=" * 60)
    
    # 1. Проверяем наличие записи
    execute_query(cursor, "SELECT id, access_token, role, full_name FROM patient_access WHERE access_token = ?;", (admin_login,))
    row = cursor.fetchone()
    
    is_postgres = bool(os.getenv("DATABASE_URL") and "postgres" in os.getenv("DATABASE_URL", "").lower())
    val_verified = True if is_postgres else 1
    
    if row:
        admin_id = row[0]
        execute_query(cursor, """
            UPDATE patient_access
            SET password_hash = ?,
                role = 'ADMIN',
                gdrive_folder_id = ?,
                full_name = ?,
                specialization = ?,
                experience_years = ?,
                is_verified = ?
            WHERE id = ?;
        """, (pw_hash, vault_folder_id, full_name, specialization, experience_years, val_verified, admin_id))
        conn.commit()
        print(f"✅ Учётная запись администратора '{admin_login}' успешно обновлена (ID: {admin_id}).")
    else:
        execute_query(cursor, """
            INSERT INTO patient_access (
                access_token, password_hash, gdrive_folder_id, role,
                full_name, specialization, experience_years, is_verified
            )
            VALUES (?, ?, ?, 'ADMIN', ?, ?, ?, ?);
        """, (admin_login, pw_hash, vault_folder_id, full_name, specialization, experience_years, val_verified))
        conn.commit()
        print(f"✅ Новая учётная запись администратора '{admin_login}' успешно создана.")
    
    # 2. Получаем список всех существующих администраторов
    execute_query(cursor, "SELECT id, access_token, full_name, created_at FROM patient_access WHERE role = 'ADMIN' ORDER BY id ASC;")
    all_admins = cursor.fetchall()
    conn.close()
    
    print("-" * 60)
    print("📋 ДОСТУПЫ АДМИНИСТРАТОРА ДЛЯ ПРОДЮСЕРА:")
    print(f"🔗 Панель управления CMS: https://цмз.site/#admin")
    print(f"👤 Логин:                 {admin_login}")
    print(f"🔑 Пароль:                {admin_pass}")
    print(f"🛡️ Роль:                  {role}")
    print("-" * 60)
    print(f"👥 ВСЕ АКТИВНЫЕ АДМИНИСТРАТОРЫ В СИСТЕМЕ ({len(all_admins)}):")
    for adm in all_admins:
        print(f"  • ID {adm[0]}: {adm[1]} ({adm[2] or 'Администратор'}) | создан: {adm[3]}")
    print("=" * 60)

if __name__ == "__main__":
    seed_producer_admin()

