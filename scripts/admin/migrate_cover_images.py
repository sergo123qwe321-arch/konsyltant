import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

import database

def migrate_covers():
    database.init_db()
    conn = database.get_connection()
    cursor = conn.cursor()
    
    print('=== MIGRATING POST COVERS ===')
    cursor.execute('SELECT id, title, cover_image_url FROM public_posts')
    posts = cursor.fetchall()
    migrated_posts = 0
    for p in posts:
        pid, title, cover = p[0], p[1], p[2] or ''
        if 'yandex' in cover.lower() or 'disk.yandex' in cover.lower():
            new_cover = '/static/images/char_a.jpg'
            database.execute_query(cursor, 'UPDATE public_posts SET cover_image_url = ? WHERE id = ?', (new_cover, pid))
            print(f'Updated post ID {pid} ({title[:30]}): {cover} -> {new_cover}')
            migrated_posts += 1
            
    print(f'Total posts migrated: {migrated_posts}')

    print('=== MIGRATING LIBRARY COVERS ===')
    cursor.execute('SELECT id, title, cover_image_url FROM public_library')
    lib = cursor.fetchall()
    migrated_lib = 0
    for l in lib:
        lid, title, cover = l[0], l[1], l[2] or ''
        if 'yandex' in cover.lower() or 'disk.yandex' in cover.lower():
            new_cover = '/static/images/char_a.jpg'
            database.execute_query(cursor, 'UPDATE public_library SET cover_image_url = ? WHERE id = ?', (new_cover, lid))
            print(f'Updated library ID {lid} ({title[:30]}): {cover} -> {new_cover}')
            migrated_lib += 1

    print(f'Total library items migrated: {migrated_lib}')
    conn.commit()
    conn.close()
    print('Cover migration completed successfully.')

if __name__ == '__main__':
    migrate_covers()
