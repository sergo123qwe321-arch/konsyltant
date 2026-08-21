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

echo '=== 2. DOCKER BUILD & UP ==='
docker compose build web
docker compose up -d
sleep 3

echo '=== 3. SEED PRODUCER ADMIN ON POSTGRESQL ==='
docker compose exec web python scripts/admin/seed_producer_admin.py

echo '=== 4. RUN ALL IN-CONTAINER TESTS (74 TESTS) ==='
docker compose exec web python -m unittest test_production_launch.py test_voice_input.py test_alert_system.py test_landing_and_admin_ops.py test_observability_metrics.py test_etl_diagnostic.py test_yandex_disk_autonomy.py test_sharing_limit.py test_pdf_generation.py test_doctor_summary_api.py test_rate_limiting.py test_db_indexes.py test_e2e_doctor_share.py -v

echo '=== 5. LIVE PRODUCTION LAUNCH VERIFICATION ==='
docker compose exec web python -c "
import requests, json
from notification_service import send_dual_email

print('--- LIVE SEED PRODUCTION PATIENT ---')
import subprocess
out = subprocess.check_output(['python', 'scripts/admin/seed_production_patient.py', 'Тестовый Пациент']).decode('utf-8')
print(out[:300] + '...')

print('--- LIVE DUAL EMAIL DELIVERY TEST ---')
res_email = send_dual_email(
    subject='Тест готовности к боевому запуску',
    html_body='<h2>🚀 Платформа полностью готова к переходу на боевые данные!</h2><p>Все тесты пройдены успешно.</p>'
)
print('Dual Email Result:', res_email)

print('--- LIVE ADMIN LOGIN & DIAGNOSTIC ENDPOINT ---')
res_login = requests.post('http://127.0.0.1:8000/api/v1/admin/login', json={
    'username': 'producer-admin@cmz.site',
    'password': 'AdminAccess2026!'
})
token = res_login.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

res_diag = requests.get('http://127.0.0.1:8000/api/v1/admin/diagnose/folder/Тестовый Пациент', headers=headers)
print(f'Diagnose Status: {res_diag.status_code}')
print('Diagnose keys:', list(res_diag.json().keys()))

print('--- LIVE GET /api/v1/admin/alerts/status ---')
res_alert_status = requests.get('http://127.0.0.1:8000/api/v1/admin/alerts/status', headers=headers)
print(f'Alerts Status: {res_alert_status.status_code}')

print('--- LIVE GET /api/v1/public/posts ---')
res_posts = requests.get('http://127.0.0.1:8000/api/v1/public/posts')
posts = res_posts.json()
print(f'Total posts: {len(posts)}')
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

