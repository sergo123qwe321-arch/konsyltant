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
    Инициализирует базу данных (PostgreSQL или SQLite) и создает таблицу patient_access.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if DATABASE_URL and psycopg2:
        auto_inc = "SERIAL PRIMARY KEY"
        date_type = "TIMESTAMP"
    else:
        auto_inc = "INTEGER PRIMARY KEY AUTOINCREMENT"
        date_type = "DATETIME"
        
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS patient_access (
            id {auto_inc},
            access_token TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            gdrive_folder_id TEXT NOT NULL,
            created_at {date_type} DEFAULT CURRENT_TIMESTAMP
        )
    """)
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
