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
sleep 4

echo '=== 3. RUN DATABASE COVER MIGRATION ==='
docker compose exec web python scripts/admin/migrate_cover_images.py

echo '=== 4. SEED PRODUCER ADMIN ON POSTGRESQL ==='
docker compose exec web python scripts/admin/seed_producer_admin.py

echo '=== 5. RUN IN-CONTAINER TESTS (85 TESTS) ==='
docker compose exec web python -m unittest test_doctor_notes_and_dashboard.py test_local_uploads.py test_community_chat.py test_technological_sovereignty.py test_production_launch.py test_voice_input.py test_alert_system.py test_landing_and_admin_ops.py test_observability_metrics.py test_etl_diagnostic.py test_yandex_disk_autonomy.py test_sharing_limit.py test_pdf_generation.py test_doctor_summary_api.py test_rate_limiting.py test_db_indexes.py test_e2e_doctor_share.py -v

echo '=== 6. LIVE PRODUCTION VERIFICATION ==='
docker compose exec web python -c "
import requests, json

print('--- LIVE COMMUNITY CHAT TEST ---')
res_chat = requests.get('http://127.0.0.1:8000/api/v1/public/chat?limit=5')
print('Public Chat Status:', res_chat.status_code)
print('Total Messages:', res_chat.json().get('total', 0))

print('--- LIVE ADMIN HEALTH CHECK ---')
res_login = requests.post('http://127.0.0.1:8000/api/v1/admin/login', json={
    'username': 'producer-admin@cmz.site',
    'password': 'AdminAccess2026!'
})
token = res_login.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
res_health = requests.get('http://127.0.0.1:8000/api/v1/admin/alerts/status', headers=headers)
print('Alerts Status:', res_health.status_code)
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
