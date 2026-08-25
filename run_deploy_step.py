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

echo '=== 4. SEED UAT FIXTURES (DOCTOR, PATIENT, ADMIN, POSTS) ==='
docker compose exec web python scripts/admin/seed_uat_fixtures.py

echo '=== 5. RUN IN-CONTAINER DISCOVER TESTS (107 TESTS) ==='
docker compose exec web python -m unittest discover -s . -p "test_*.py" -v

echo '=== 6. LIVE PRODUCTION VERIFICATION ==='
docker compose exec web python -c "
import requests, json

print('--- 1. LIVE ADMIN LOGIN ---')
res_admin = requests.post('http://127.0.0.1:8000/api/v1/admin/login', json={
    'username': 'producer-admin@cmz.site',
    'password': 'AdminAccess2026!'
})
print('Admin Login Status:', res_admin.status_code)
admin_token = res_admin.json().get('access_token')
admin_headers = {'Authorization': f'Bearer {admin_token}'}

print('--- 2. LIVE DOCTOR LOGIN ---')
res_doc = requests.post('http://127.0.0.1:8000/api/v1/doctor/login', json={
    'email': 'producer@cmz.site',
    'password': 'TestAccess2026!'
})
print('Doctor Login Status:', res_doc.status_code)

print('--- 3. LIVE PATIENT LOGIN (BY TOKEN & EMAIL) ---')
res_pat_token = requests.post('http://127.0.0.1:8000/api/login', json={
    'token': 'test_patient_token_2026',
    'password': 'PatientAccess2026!'
})
print('Patient Login by Token Status:', res_pat_token.status_code)

res_pat_email = requests.post('http://127.0.0.1:8000/api/login', json={
    'token': 'patient@cmz.site',
    'password': 'PatientAccess2026!'
})
print('Patient Login by Email Status:', res_pat_email.status_code)

print('--- 4. LIVE POSTS FEED ---')
res_posts = requests.get('http://127.0.0.1:8000/api/v1/public/posts')
print('Public Posts Status:', res_posts.status_code, 'Count:', len(res_posts.json()))

print('--- 5. LIVE GUEST CHAT MESSAGE POST & FEED ---')
res_guest = requests.post('http://127.0.0.1:8000/api/v1/public/chat', json={
    'message': 'Привет от гостя! Проверка чата v7.1',
    'author_name': 'Гость Тестировщик'
})
print('Guest Chat Post Status:', res_guest.status_code, res_guest.json().get('message', {}).get('author_role'))

res_chat = requests.get('http://127.0.0.1:8000/api/v1/public/chat?limit=5')
print('Public Chat Status:', res_chat.status_code, 'Total Messages:', res_chat.json().get('total', 0))

print('--- 6. LIVE ALERTS & HEALTH MONITORING ---')
res_health = requests.get('http://127.0.0.1:8000/api/v1/admin/alerts/status', headers=admin_headers)
print('Alerts System Status:', res_health.status_code)
"

echo '=== 7. DOCKER COMPOSE PS & WEB LOGS ==='
docker compose ps
docker logs --tail 30 konsyltant_web
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
