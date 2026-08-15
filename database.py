import sqlite3
import bcrypt
import secrets
import os

try:
    import psycopg2
except ImportError:
    psycopg2 = None

DB_FILE = "konsyltant.db"
DATABASE_URL = os.getenv("DATABASE_URL")

# Render.com иногда выдает строку, начинающуюся с postgres://, 
# которая устарела для современных драйверов, поэтому принудительно заменяем на postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_connection():
    if DATABASE_URL and psycopg2:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(DB_FILE)

def execute_query(cursor, query, params=()):
    if DATABASE_URL and psycopg2:
        # В PostgreSQL используется синтаксис %s вместо ?
        query = query.replace("?", "%s")
    cursor.execute(query, params)

def init_db():
    """
    Инициализирует базу данных (PostgreSQL или SQLite) и создает таблицы.
    Включает автоматическую миграцию схемы (добавление новых колонок в patient_access).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    is_postgres = bool(DATABASE_URL and psycopg2)
    if is_postgres:
        auto_inc = "SERIAL PRIMARY KEY"
        date_type = "TIMESTAMP"
        bool_type = "BOOLEAN"
    else:
        auto_inc = "INTEGER PRIMARY KEY AUTOINCREMENT"
        date_type = "DATETIME"
        bool_type = "BOOLEAN"
        
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_access (
            id {auto_inc},
            access_token TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            gdrive_folder_id TEXT NOT NULL,
            created_at {date_type} DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Миграция: проверка и добавление новых колонок role и is_verified
    if is_postgres:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='patient_access' AND column_name='role'")
        role_exists = cursor.fetchone() is not None
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='patient_access' AND column_name='is_verified'")
        verified_exists = cursor.fetchone() is not None
    else:
        cursor.execute("PRAGMA table_info(patient_access)")
        columns = [col[1] for col in cursor.fetchall()]
        role_exists = 'role' in columns
        verified_exists = 'is_verified' in columns

    if not role_exists:
        cursor.execute("ALTER TABLE patient_access ADD COLUMN role VARCHAR DEFAULT 'PATIENT'")
    
    if not verified_exists:
        # Для существующих записей ставим TRUE по умолчанию (так как это уже зарегистрированные пациенты)
        cursor.execute(f"ALTER TABLE patient_access ADD COLUMN is_verified {bool_type} DEFAULT TRUE")

    # Добавляем колонки для публичного профиля врачей
    if is_postgres:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='patient_access' AND column_name='full_name'")
        profile_exists = cursor.fetchone() is not None
    else:
        cursor.execute("PRAGMA table_info(patient_access)")
        columns = [col[1] for col in cursor.fetchall()]
        profile_exists = 'full_name' in columns
        
    if not profile_exists:
        cursor.execute("ALTER TABLE patient_access ADD COLUMN full_name TEXT")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN specialization TEXT")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN experience_years INTEGER")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN avatar_url TEXT")

    # Создание таблицы шеринга доступов
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_share_grants (
            grant_id {auto_inc},
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            share_token VARCHAR UNIQUE NOT NULL,
            expires_at {date_type} NOT NULL,
            is_active {bool_type} DEFAULT TRUE,
            created_at {date_type} DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patient_access(id),
            FOREIGN KEY (doctor_id) REFERENCES patient_access(id)
        )
    """)
    
    # Таблицы публичного контента
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS public_services (
            id {auto_inc},
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            icon_name TEXT,
            created_at {date_type} DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS public_events (
            id {auto_inc},
            title TEXT NOT NULL,
            description TEXT,
            event_date TEXT,
            location TEXT,
            image_url TEXT,
            created_at {date_type} DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS public_posts (
            id {auto_inc},
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            author_id INTEGER,
            tags TEXT,
            created_at {date_type} DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Seeding (Начальное заполнение)
    cursor.execute("SELECT COUNT(*) FROM public_services")
    if cursor.fetchone()[0] == 0:
        execute_query(cursor, "INSERT INTO public_services (title, description, category, icon_name) VALUES (?, ?, ?, ?)",
                       ("Консультация педиатра", "Первичный осмотр и постановка диагноза", "Медицина", "stethoscope"))
        execute_query(cursor, "INSERT INTO public_services (title, description, category, icon_name) VALUES (?, ?, ?, ?)",
                       ("Логопедическое занятие", "Коррекция речи и звукопроизношения", "Развитие", "smile"))

    cursor.execute("SELECT COUNT(*) FROM public_events")
    if cursor.fetchone()[0] == 0:
        execute_query(cursor, "INSERT INTO public_events (title, description, event_date, location, image_url) VALUES (?, ?, ?, ?, ?)",
                       ("День открытых дверей", "Знакомство с клиникой и врачами", "2026-09-01", "Главный холл", ""))
        
    cursor.execute("SELECT COUNT(*) FROM public_posts")
    if cursor.fetchone()[0] == 0:
        execute_query(cursor, "INSERT INTO public_posts (title, summary, content, tags) VALUES (?, ?, ?, ?)",
                       ("Как подготовить ребенка к школе", "Советы психолога", "Полный текст статьи...", '["психология", "школа"]'))

    cursor.execute("SELECT COUNT(*) FROM patient_access WHERE role = 'DOCTOR'")
    if cursor.fetchone()[0] == 0:
        token = secrets.token_urlsafe(32)
        pwd = bcrypt.hashpw(b'doc_password', bcrypt.gensalt()).decode('utf-8')
        val_is_verified = True
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, is_verified, full_name, specialization, experience_years)
            VALUES (?, ?, ?, 'DOCTOR', ?, ?, ?, ?)
        """, (token, pwd, 'fake_folder', val_is_verified, 'Доктор Айболит', 'Главный педиатр', 15))
    
    conn.commit()
    conn.close()

def create_patient_access(password: str, gdrive_folder_id: str) -> str:
    """
    Создает новый доступ, хэширует пароль, генерирует уникальный токен.
    Возвращает access_token.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    access_token = secrets.token_urlsafe(32)
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    execute_query(cursor, """
        INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id)
        VALUES (?, ?, ?)
    """, (access_token, password_hash, gdrive_folder_id))
    
    conn.commit()
    conn.close()
    return access_token

def verify_access(access_token: str, password: str) -> str:
    """
    Проверяет токен и пароль. 
    Возвращает gdrive_folder_id при успехе, иначе None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    execute_query(cursor, """
        SELECT password_hash, gdrive_folder_id FROM patient_access 
        WHERE access_token = ?
    """, (access_token,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        stored_hash = row[0]
        gdrive_folder_id = row[1]
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return gdrive_folder_id
            
    return None

def token_exists(access_token: str) -> bool:
    """
    Проверяет, существует ли токен в базе данных.
    """
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT 1 FROM patient_access WHERE access_token = ?", (access_token,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def folder_exists(gdrive_folder_id: str) -> bool:
    """
    Проверяет, зарегистрирована ли папка в базе данных.
    """
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT 1 FROM patient_access WHERE gdrive_folder_id = ?", (gdrive_folder_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_public_services():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, category, icon_name FROM public_services")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "category": r[3], "icon_name": r[4]} for r in rows]

def get_public_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, event_date, location, image_url FROM public_events")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "event_date": r[3], "location": r[4], "image_url": r[5]} for r in rows]

def get_public_posts(tag=None):
    conn = get_connection()
    cursor = conn.cursor()
    if tag:
        execute_query(cursor, "SELECT id, title, summary, content, tags, created_at FROM public_posts WHERE tags LIKE ?", (f'%"{tag}"%',))
    else:
        execute_query(cursor, "SELECT id, title, summary, content, tags, created_at FROM public_posts")
    rows = cursor.fetchall()
    conn.close()
    import json
    res = []
    for r in rows:
        try:
            tags_list = json.loads(r[4]) if r[4] else []
        except:
            tags_list = []
        res.append({"id": r[0], "title": r[1], "summary": r[2], "content": r[3], "tags": tags_list, "created_at": str(r[5])})
    return res

def get_public_doctors():
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT id, full_name, specialization, experience_years, avatar_url FROM patient_access WHERE role = 'DOCTOR' AND is_verified = TRUE")
    rows = cursor.fetchall()
    if not rows:
        execute_query(cursor, "SELECT id, full_name, specialization, experience_years, avatar_url FROM patient_access WHERE role = 'DOCTOR' AND is_verified = 1")
        rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "full_name": r[1], "specialization": r[2], "experience_years": r[3], "avatar_url": r[4]} for r in rows]
