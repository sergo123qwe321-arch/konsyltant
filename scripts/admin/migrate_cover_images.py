import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
load_dotenv()
from database import init_db, get_connection, execute_query

def migrate_cover_images():
    print('=' * 60)
    print('РЕСУРСНАЯ МИГРАЦИЯ ОБЛОЖЕК И МЕДИА-ССЫЛОК (152-ФЗ / LOCAL STATIC)')
    print('=' * 60)
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, 'SELECT id, title, cover_image_url, video_url FROM public_posts')
    posts = cursor.fetchall()
    migrated_posts = 0
    for row in posts:
        post_id, title, cover_url, video_url = row[0], row[1], row[2] or '', row[3] or ''
        need_update = False
        new_cover = cover_url
        new_video = video_url
        if any(bad in (cover_url or '').lower() for bad in ['yadi.sk', 'disk.yandex', 'disk:/uploads', 'downloader.disk']):
            new_cover = '/static/images/char_a.jpg'
            need_update = True
        if any(bad in (video_url or '').lower() for bad in ['yadi.sk', 'disk.yandex', 'disk:/uploads', 'downloader.disk']):
            new_video = ''
            need_update = True
        if need_update:
            execute_query(cursor, 'UPDATE public_posts SET cover_image_url = ?, video_url = ? WHERE id = ?', (new_cover, new_video, post_id))
            migrated_posts += 1
    execute_query(cursor, 'SELECT id, title, cover_image_url, video_url FROM public_library')
    library_items = cursor.fetchall()
    migrated_lib = 0
    for row in library_items:
        lib_id, title, cover_url, video_url = row[0], row[1], row[2] or '', row[3] or ''
        need_update = False
        new_cover = cover_url
        new_video = video_url
        if any(bad in (cover_url or '').lower() for bad in ['yadi.sk', 'disk.yandex', 'disk:/uploads', 'downloader.disk']):
            new_cover = '/static/images/char_o.jpg'
            need_update = True
        if any(bad in (video_url or '').lower() for bad in ['yadi.sk', 'disk.yandex', 'disk:/uploads', 'downloader.disk']):
            new_video = ''
            need_update = True
        if need_update:
            execute_query(cursor, 'UPDATE public_library SET cover_image_url = ?, video_url = ? WHERE id = ?', (new_cover, new_video, lib_id))
            migrated_lib += 1
    conn.commit()
    conn.close()
    uploads_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')), 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    total_size = sum(os.path.getsize(os.path.join(r, f)) for r, d, files in os.walk(uploads_dir) for f in files if f != '.gitkeep')
    print(f'Миграция завершена: обновлено постов {migrated_posts}, материалов {migrated_lib}')
    print(f'Размер static/uploads/: {total_size} байт')

if __name__ == '__main__':
    migrate_cover_images()
