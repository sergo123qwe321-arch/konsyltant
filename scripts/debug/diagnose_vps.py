import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('159.194.232.74', port=22, username='root', password=os.getenv('BEGET_SSH_PASSWORD'), timeout=10)

script = """
echo '=== 1. LOGS (LAST 100 LINES) ==='
docker compose -f /root/konsyltant/docker-compose.yml logs --tail 100 web

echo '=== 2. DATABASE COUNTS IN POSTGRES ==='
docker compose -f /root/konsyltant/docker-compose.yml exec web python -c "
from database import get_connection
conn = get_connection()
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM public_posts;')
print('public_posts count:', c.fetchone()[0])
c.execute('SELECT COUNT(*) FROM public_leads;')
print('public_leads count:', c.fetchone()[0])
c.execute('SELECT id, title, created_at FROM public_posts ORDER BY id DESC LIMIT 5;')
print('recent posts:', c.fetchall())
c.execute('SELECT id, name, phone, created_at FROM public_leads ORDER BY id DESC LIMIT 5;')
print('recent leads:', c.fetchall())
conn.close()
"

echo '=== 3. CURL TEST ADMIN LOGIN & ENDPOINTS ==='
docker compose -f /root/konsyltant/docker-compose.yml exec web python -c "
import requests, json

print('1. Admin Login:')
res = requests.post('http://127.0.0.1:8000/api/v1/admin/login', json={'username': 'producer-admin@cmz.site', 'password': 'AdminAccess2026!'})
print('Status:', res.status_code, res.text[:200])
token = res.json().get('access_token')

headers = {'Authorization': f'Bearer {token}'}

print('2. GET /api/v1/admin/leads:')
res_leads = requests.get('http://127.0.0.1:8000/api/v1/admin/leads', headers=headers)
print('Status:', res_leads.status_code, 'Count:', len(res_leads.json()) if res_leads.status_code == 200 else res_leads.text)

print('3. POST /api/v1/admin/posts:')
post_payload = {'title': 'Тестовый пост диагностики', 'summary': 'Краткий анонс', 'content': 'Полный текст', 'tags': ['Тест']}
res_post = requests.post('http://127.0.0.1:8000/api/v1/admin/posts', headers=headers, json=post_payload)
print('Status:', res_post.status_code, res_post.text)

print('4. GET /api/v1/public/posts:')
res_pub = requests.get('http://127.0.0.1:8000/api/v1/public/posts')
print('Status:', res_pub.status_code, 'Count:', len(res_pub.json()) if res_pub.status_code == 200 else res_pub.text)
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

