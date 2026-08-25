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

echo '=== 5. RUN IN-CONTAINER DISCOVER TESTS (107 TESTS) ==='
docker compose exec web python -m unittest discover -s . -p "test_*.py" -v

echo '=== 6. LIVE PRODUCTION VERIFICATION (v7.1-production) ==='
docker compose exec web python -c "
import requests, json

print('--- 1. LIVE ADMIN LOGIN ---')
res_login = requests.post('http://127.0.0.1:8000/api/v1/admin/login', json={
    'username': 'producer-admin@cmz.site',
    'password': 'AdminAccess2026!'
})
print('Admin Login Status:', res_login.status_code)
token = res_login.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

print('--- 2. LIVE DOCTORS LIST (ADMIN API) ---')
res_docs = requests.get('http://127.0.0.1:8000/api/v1/admin/doctors', headers=headers)
print('Admin Doctors Status:', res_docs.status_code, 'Count:', len(res_docs.json().get('doctors', [])))

print('--- 3. LIVE GUEST CHAT MESSAGE POST ---')
res_guest = requests.post('http://127.0.0.1:8000/api/v1/public/chat', json={
    'message': 'Тестовое сообщение гостя после деплоя v7.1',
    'author_name': 'Проверка Деплоя'
})
print('Guest Chat Post Status:', res_guest.status_code, res_guest.json().get('message', {}).get('author_role'))

print('--- 4. LIVE PUBLIC CHAT FEED ---')
res_chat = requests.get('http://127.0.0.1:8000/api/v1/public/chat?limit=5')
print('Public Chat Status:', res_chat.status_code, 'Total Messages:', res_chat.json().get('total', 0))

print('--- 5. LIVE MEDIA URL & HEALTH MONITORING ---')
res_health = requests.get('http://127.0.0.1:8000/api/v1/admin/alerts/status', headers=headers)
print('Alerts System Status:', res_health.status_code)
"

echo '=== 7. DOCKER COMPOSE PS & WEB LOGS ==='
docker compose ps
docker logs --tail 30 konsyltant_web
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
