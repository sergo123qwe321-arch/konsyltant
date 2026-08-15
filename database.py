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
    Включает автоматическую миграцию схемы для существующих баз данных.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    is_postgres = bool(DATABASE_URL and psycopg2)
    if is_postgres:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_access (
                id SERIAL PRIMARY KEY,
                access_token TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                gdrive_folder_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role VARCHAR(20) DEFAULT 'PATIENT',
                full_name VARCHAR(100) DEFAULT '',
                specialization VARCHAR(100) DEFAULT '',
                experience_years INTEGER DEFAULT 0,
                avatar_url VARCHAR(255) DEFAULT '',
                is_verified BOOLEAN DEFAULT FALSE
            )
        """)
        # Гарантируем миграцию колонок для существующих таблиц на сервере
        cursor.execute("ALTER TABLE patient_access ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'PATIENT'")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN IF NOT EXISTS full_name VARCHAR(100) DEFAULT ''")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN IF NOT EXISTS specialization VARCHAR(100) DEFAULT ''")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(255) DEFAULT ''")
        cursor.execute("ALTER TABLE patient_access ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE")
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_services (
                id SERIAL PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                description TEXT,
                category VARCHAR(50),
                icon_name VARCHAR(50)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_events (
                id SERIAL PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                description TEXT,
                event_date VARCHAR(50),
                location VARCHAR(100),
                image_url VARCHAR(255)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                summary TEXT,
                content TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_leads (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                child_age VARCHAR(50) DEFAULT '',
                message TEXT DEFAULT '',
                status VARCHAR(30) DEFAULT 'NEW',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_token TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                gdrive_folder_id TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT DEFAULT 'PATIENT',
                full_name TEXT DEFAULT '',
                specialization TEXT DEFAULT '',
                experience_years INTEGER DEFAULT 0,
                avatar_url TEXT DEFAULT '',
                is_verified BOOLEAN DEFAULT 0
            )
        """)
        cursor.execute("PRAGMA table_info(patient_access)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        sqlite_cols = [
            ("role", "TEXT DEFAULT 'PATIENT'"),
            ("full_name", "TEXT DEFAULT ''"),
            ("specialization", "TEXT DEFAULT ''"),
            ("experience_years", "INTEGER DEFAULT 0"),
            ("avatar_url", "TEXT DEFAULT ''"),
            ("is_verified", "BOOLEAN DEFAULT 0")
        ]
        for col_name, col_def in sqlite_cols:
            if col_name not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE patient_access ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass
        conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                icon_name TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_date TEXT,
                location TEXT,
                image_url TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                content TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                child_age TEXT DEFAULT '',
                message TEXT DEFAULT '',
                status TEXT DEFAULT 'NEW',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    # 1. Сидирование врачей
    cursor.execute("SELECT COUNT(*) FROM patient_access WHERE role = 'DOCTOR'")
    if cursor.fetchone()[0] < 3:
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(b"doctor123", salt).decode('utf-8')
        val_verified = True if is_postgres else 1
        # Очистим старые неполные данные врачей
        cursor.execute("DELETE FROM patient_access WHERE role = 'DOCTOR'")
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, full_name, specialization, experience_years, avatar_url, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("doc_anna", pw_hash, "folder_doc_anna", "DOCTOR", "Анна Сергеевна Волкова", "Ведущий нейропсихолог", 10, "", val_verified))
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, full_name, specialization, experience_years, avatar_url, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("doc_mikhail", pw_hash, "folder_doc_mikhail", "DOCTOR", "Михаил Андреевич Морозов", "Клинический логопед-дефектолог", 8, "", val_verified))
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, full_name, specialization, experience_years, avatar_url, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("doc_elena", pw_hash, "folder_doc_elena", "DOCTOR", "Елена Викторовна Смирнова", "Детский психотерапевт", 12, "", val_verified))

    # 2. Сидирование услуг
    cursor.execute("SELECT COUNT(*) FROM public_services")
    if cursor.fetchone()[0] < 3:
        cursor.execute("DELETE FROM public_services")
        execute_query(cursor, "INSERT INTO public_services (title, description, category, icon_name) VALUES (?, ?, ?, ?)",
                       ("Нейропсихологическая диагностика", "Комплексное исследование высших психических функций ребенка", "Диагностика", "brain"))
        execute_query(cursor, "INSERT INTO public_services (title, description, category, icon_name) VALUES (?, ?, ?, ?)",
                       ("Запуск и коррекция речи", "Индивидуальные занятия с логопедом в игровом сказочном формате", "Логопедия", "smile"))
        execute_query(cursor, "INSERT INTO public_services (title, description, category, icon_name) VALUES (?, ?, ?, ?)",
                       ("Детская психотерапия", "Бережная проработка тревожности, страхов и адаптация к социуму", "Психотерапия", "heart"))

    # 3. Сидирование событий
    cursor.execute("SELECT COUNT(*) FROM public_events")
    if cursor.fetchone()[0] < 2:
        cursor.execute("DELETE FROM public_events")
        execute_query(cursor, "INSERT INTO public_events (title, description, event_date, location, image_url) VALUES (?, ?, ?, ?, ?)",
                       ("Мастер-класс: Игры, развивающие мозг", "Интерактивная встреча с нейропсихологом для увлеченных родителей", "2026-08-20 18:00", "Игровая гостиная", ""))
        execute_query(cursor, "INSERT INTO public_events (title, description, event_date, location, image_url) VALUES (?, ?, ?, ?, ?)",
                       ("Встреча Клуба: Пойми меня без слов", "Разбор детской тревожности и возрастных кризисов", "2026-08-25 15:30", "Уютный зал", ""))
        
    # 4. Сидирование 3 экспертных статей блога
    cursor.execute("SELECT COUNT(*) FROM public_posts")
    if cursor.fetchone()[0] < 3:
        cursor.execute("DELETE FROM public_posts")
        post1_content = ("Речевое развитие ребенка - это не механическое повторение слогов за взрослым, а сложный нейродинамический процесс, неразрывно связанный с крупной моторикой, дыханием и эмоциональным контактом.\n\n"
                         "5 проверенных упражнений от ведущих нейропсихологов центра:\n\n"
                         "1. Задуй свечу / Буря в стакане\n"
                         "Формирование правильного речевого выдоха - основа четкой дикции. Дуем на бумажные кораблики в ванне, через трубочку в воду или на свечу с разного расстояния.\n\n"
                         "2. Эхо в горах (Звукоподражание)\n"
                         "Используем эмоциональные короткие звуки в контексте игры: машинка едет (Би-би!), часики тикают (Тик-так), дождик капает (Кап-кап). Важно смотреть ребенку в глаза на уровне его роста.\n\n"
                         "3. Ритмический оркестр\n"
                         "Стучим деревянными ложками или ладошками по коленям под простые стишки. Ритм напрямую стимулирует речевые центры Брока и Вернике.\n\n"
                         "4. Полоса препятствий с озвучкой\n"
                         "Перешагиваем через подушки со звуками Топ-топ, прыгаем Прыг-скок. Связка движения и звука ускоряет запуск речи.\n\n"
                         "5. Угадай, кто в домике\n"
                         "Прячем игрушечных животных под платочек и просим угадать по звукам: Му-у, Гав-гав, Ква-ква.")
        
        post2_content = ("Гиперактивность и импульсивность - это не вредность ребенка, а особенность созревания лобных долей головного мозга, отвечающих за функцию самоконтроля и торможения.\n\n"
                         "Нейроигры для тренировки функции торможения:\n\n"
                         "1. Замри - Отомри (Стоп-игра)\n"
                         "Под веселую музыку ребенок активно танцует или бегает, но по хлопку или слову Замри! мгновенно застывает в любой позе. Это напрямую тренирует тормозные механизмы коры.\n\n"
                         "2. Канатоходец\n"
                         "Наклеиваем на полу малярный скотч (или выкладываем веревочку). Задача - пройти точно по линии, удерживая равновесие и неся в руках стаканчик с водой или мячик.\n\n"
                         "3. Ритмические хлопки и шифры\n"
                         "Один хлопок - ребенок топает, два хлопка - прыгает, три - садится на корточки. Развивает произвольное внимание и слуховой контроль.\n\n"
                         "4. Тяжелое одеяло и объятия-кокон\n"
                         "Глубокое проприоцептивное давление перед сном помогает нервной системе переключиться из режима возбуждения в режим восстановления.")

        post3_content = ("Когда ребенок через 15 минут выполнения уроков начинает крутиться, ложиться на стол или допускать глупые ошибки - чаще всего речь идет о дефиците нейродинамики (первый энергетический блок мозга по А.Р. Лурия).\n\n"
                         "Как помочь мозгу включиться:\n\n"
                         "1. Кинезиологическое упражнение Кулак - Ребро - Ладонь\n"
                         "Ребенок последовательно меняет положение ладони на столе: сжатый кулак, ладонь ребром, раскрытая ладонь. Повторяем сначала ведущей рукой, затем другой, затем двумя руками одновременно.\n\n"
                         "2. Двуручное зеркальное рисование\n"
                         "Рисуем в воздухе или на листе бумаги симметричные фигуры (сердечки, круги, домики) обеими руками одновременно. Это активизирует межполушарные связи (мозолистое тело).\n\n"
                         "3. Нейропеременки каждые 20 минут\n"
                         "3-минутная физическая пауза: потягивания, перекрестные шаги (локоть к противоположному колену), стакан чистой воды.\n\n"
                         "4. Правильное сенсорное окружение\n"
                         "Уберите визуальный шум с рабочего стола: оставьте только один учебник и одну тетрадь, чтобы не перегружать поле внимания.")

        execute_query(cursor, "INSERT INTO public_posts (title, summary, content, tags) VALUES (?, ?, ?, ?)",
                       ("Как мягко подтолкнуть речь: 5 речевых игр от нейропсихолога без принуждения и слез",
                        "Простые и бережные практики для домашних занятий: дыхательные упражнения со свечками, мыльными пузырями и ритмические игры на звукоподражание (Би-би, Тик-так, Кап-кап).",
                        post1_content,
                        '["Развитие речи", "Игры"]'))

        execute_query(cursor, "INSERT INTO public_posts (title, summary, content, tags) VALUES (?, ?, ?, ?)",
                       ("Энергия в мирное русло: нейроигры для сброса гиперактивности и развития самоконтроля",
                        "Игры Замри-отомри, Канатоходец и Ритмические хлопки, которые помогают ребенку научиться торможению нервной системы, осознанию тела и снятию эмоционального перегруза.",
                        post2_content,
                        '["Эмоции и поведение", "Игры"]'))

        execute_query(cursor, "INSERT INTO public_posts (title, summary, content, tags) VALUES (?, ?, ?, ?)",
                       ("Быстро устает и отвлекается в школе? Понимаем нейродинамические особенности ребенка и помогаем мозгу без крика",
                        "Кинезиологическая гимнастика Кулак-ребро-ладонь, нейропеременки и режим сенсорной разгрузки для поддержки первого энергетического блока мозга.",
                        post3_content,
                        '["Нейродинамика", "Игры"]'))

    # 5. Сидирование Администратора CMS
    cursor.execute("SELECT COUNT(*) FROM patient_access WHERE role = 'ADMIN'")
    if cursor.fetchone()[0] == 0:
        admin_token = "admin"
        admin_pwd = os.getenv("ADMIN_PASSWORD", "admin123")
        pwd = bcrypt.hashpw(admin_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        val_verified = True if is_postgres else 1
        execute_query(cursor, """
            INSERT INTO patient_access (access_token, password_hash, gdrive_folder_id, role, is_verified, full_name, specialization, experience_years)
            VALUES (?, ?, 'admin_vault', 'ADMIN', ?, 'Администратор Клиники', 'Управление CMS', 10)
        """, (admin_token, pwd, val_verified))
    
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

def create_lead(name: str, phone: str, child_age: str = "", message: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, """
        INSERT INTO public_leads (name, phone, child_age, message)
        VALUES (?, ?, ?, ?)
    """, (name, phone, child_age, message))
    conn.commit()
    conn.close()
    return 1

def get_all_leads():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, child_age, message, status, created_at FROM public_leads ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "name": r[1],
            "phone": r[2],
            "child_age": r[3],
            "message": r[4],
            "status": r[5],
            "created_at": str(r[6])
        }
        for r in rows
    ]

def create_public_post(title: str, summary: str, content: str, tags: list) -> int:
    import json
    conn = get_connection()
    cursor = conn.cursor()
    tags_json = json.dumps(tags, ensure_ascii=False)
    execute_query(cursor, """
        INSERT INTO public_posts (title, summary, content, tags)
        VALUES (?, ?, ?, ?)
    """, (title, summary, content, tags_json))
    conn.commit()
    conn.close()
    return 1

def update_public_post(post_id: int, title: str, summary: str, content: str, tags: list) -> bool:
    import json
    conn = get_connection()
    cursor = conn.cursor()
    tags_json = json.dumps(tags, ensure_ascii=False)
    execute_query(cursor, """
        UPDATE public_posts
        SET title = ?, summary = ?, content = ?, tags = ?
        WHERE id = ?
    """, (title, summary, content, tags_json, post_id))
    conn.commit()
    conn.close()
    return True

def delete_public_post(post_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "DELETE FROM public_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return True

def get_post_by_id(post_id: int):
    import json
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT id, title, summary, content, tags, created_at FROM public_posts WHERE id = ?", (post_id,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    try:
        tags_list = json.loads(r[4]) if r[4] else []
    except:
        tags_list = []
    return {"id": r[0], "title": r[1], "summary": r[2], "content": r[3], "tags": tags_list, "created_at": str(r[5])}

def verify_admin_credentials(username: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, """
        SELECT password_hash FROM patient_access
        WHERE access_token = ? AND role = 'ADMIN'
    """, (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        stored_hash = row[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True
    return False
