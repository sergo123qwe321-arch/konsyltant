import os
import sys
import json
from dotenv import load_dotenv

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()

from database import init_db, get_connection, execute_query

POSTS_FIXTURES = [
    {
        "title": "Новая платформа запущена",
        "summary": "Рады приветствовать родителей и специалистов в обновленной цифровой среде Центра.",
        "content": "Мы рады сообщить об официальном запуске единой цифровой платформы Центра ментального здоровья детей «Маленькая Страна»! Платформа объединяет персональное ИИ-сопровождение, защищенный обмен медицинскими данными по 152-ФЗ и экспертные консультации специалистов.",
        "tags": ["Новости", "Платформа"],
        "cover_image_url": "",
        "video_url": ""
    },
    {
        "title": "Добавлена первая группа родителей",
        "summary": "Первые семьи получили доступ к персональным ИИ-консультациям по медицинским картам.",
        "content": "Первая группа родителей успешно подключилась к личному кабинету. Семьи могут круглосуточно задавать вопросы ИИ-Консультанту по индивидуальным медицинским документам и получать структурированные расшифровки анализов.",
        "tags": ["Семья", "ИИ-Консультант"],
        "cover_image_url": "",
        "video_url": ""
    },
    {
        "title": "У нас первый доктор",
        "summary": "Клинический консилиум центра пополнился ведущим детским неврологом.",
        "content": "К нашему клиническому консилиуму присоединился ведущий детский невролог с высшей квалификационной категорией. Доктор доступен для анализа динамики развития, формирования расширенных выписок и онлайн-консилиума.",
        "tags": ["Врачи", "Неврология"],
        "cover_image_url": "",
        "video_url": ""
    }
]

def seed_production_posts():
    print("=" * 60)
    print("🚀 СИДИРОВАНИЕ СВЕЖИХ ПОСТОВ В СЕКЦИЮ «НОВЫЕ ПОСТЫ»")
    print("=" * 60)
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    for item in POSTS_FIXTURES:
        execute_query(cursor, "SELECT id FROM public_posts WHERE title = ?", (item["title"],))
        row = cursor.fetchone()
        tags_json = json.dumps(item["tags"], ensure_ascii=False)
        
        if row:
            post_id = row[0]
            execute_query(cursor, """
                UPDATE public_posts
                SET summary = ?, content = ?, tags = ?, cover_image_url = ?, video_url = ?
                WHERE id = ?
            """, (item["summary"], item["content"], tags_json, item["cover_image_url"], item["video_url"], post_id))
            print(f"✅ Пост '{item['title']}' обновлен (ID: {post_id}).")
        else:
            execute_query(cursor, """
                INSERT INTO public_posts (title, summary, content, tags, cover_image_url, video_url, attachments)
                VALUES (?, ?, ?, ?, ?, ?, '[]')
            """, (item["title"], item["summary"], item["content"], tags_json, item["cover_image_url"], item["video_url"]))
            print(f"✅ Пост '{item['title']}' успешно создан.")
            
    conn.commit()
    conn.close()
    print("=" * 60)
    print("🎉 Сидирование постов завершено успешно!")
    print("=" * 60)

if __name__ == "__main__":
    seed_production_posts()
