import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('159.194.232.74', port=22, username='root', password=os.getenv('BEGET_SSH_PASSWORD'), timeout=10)

script = """
cd /root/konsyltant
echo '=== 1. FETCH & RESET ==='
git fetch origin main
git reset --hard origin/main
git log -n 1 --oneline

echo '=== 2. LINT NO TXT LOGS ==='
python3 scripts/lint_no_txt_logs.py

echo '=== 3. DOCKER BUILD & UP ==='
docker compose build web
docker compose up -d
sleep 4

echo '=== 4. SEED PRODUCER ADMIN ON POSTGRESQL ==='
docker compose exec web python scripts/admin/seed_producer_admin.py

echo '=== 5. RUN IN-CONTAINER DISCOVER TESTS (100 TESTS) ==='
docker compose exec web python -m unittest discover -s . -p "test_*.py" -v

echo '=== 6. LIVE PRODUCTION VERIFICATION (v7.1-production) ==='
docker compose exec web python -c "
import requests, json

print('--- 1. LIVE ADMIN LOGIN & MEDIA URL VALIDATION ---')
res_login = requests.post('http://127.0.0.1:8000/api/v1/admin/login', json={
    'username': 'producer-admin@cmz.site',
    'password': 'AdminAccess2026!'
})
print('Admin Login Status:', res_login.status_code)
token = res_login.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

res_media = requests.post('http://127.0.0.1:8000/api/v1/admin/media-url', headers=headers, json={
    'url': 'https://rutube.ru/video/123456/',
    'type': 'video'
})
print('Media URL Validation Status:', res_media.status_code, res_media.json())

print('--- 2. LIVE MODERATION QUEUE CHECK ---')
res_mod = requests.get('http://127.0.0.1:8000/api/v1/admin/chat/moderation', headers=headers)
print('Moderation Queue Status:', res_mod.status_code, 'Unapproved count:', len(res_mod.json().get('unapproved_messages', [])))

print('--- 3. LIVE PUBLIC CHAT FEED ---')
res_chat = requests.get('http://127.0.0.1:8000/api/v1/public/chat?limit=5')
print('Public Chat Status:', res_chat.status_code, 'Total Messages:', res_chat.json().get('total', 0))

print('--- 4. LIVE ALERTS & HEALTH MONITORING ---')
res_health = requests.get('http://127.0.0.1:8000/api/v1/admin/alerts/status', headers=headers)
print('Alerts System Status:', res_health.status_code)
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

