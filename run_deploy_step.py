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

echo '=== 4. RUN ALL IN-CONTAINER TESTS (63 TESTS) ==='
docker compose exec web python -m unittest test_alert_system.py test_landing_and_admin_ops.py test_observability_metrics.py test_etl_diagnostic.py test_yandex_disk_autonomy.py test_sharing_limit.py test_pdf_generation.py test_doctor_summary_api.py test_rate_limiting.py test_db_indexes.py test_e2e_doctor_share.py -v

echo '=== 5. LIVE VERIFICATION OF ADMIN LOGIN, ALERTS & PUBLIC POSTS ==='
docker compose exec web python -c "
import requests, json

print('--- LIVE ADMIN LOGIN (PRODUCER) ---')
res_login = requests.post('http://127.0.0.1:8000/api/v1/admin/login', json={
    'username': 'producer-admin@cmz.site',
    'password': 'AdminAccess2026!'
})
print(f'Status: {res_login.status_code}')
data = res_login.json()
print(json.dumps(data, ensure_ascii=False, indent=2))

token = data.get('access_token')
headers = {'Authorization': f'Bearer {token}'}

print('--- LIVE POST /api/v1/admin/alerts/test (SEND DUAL EMAIL) ---')
res_alert = requests.post('http://127.0.0.1:8000/api/v1/admin/alerts/test', headers=headers)
print(f'Status: {res_alert.status_code}')
print(json.dumps(res_alert.json(), ensure_ascii=False, indent=2))

print('--- LIVE GET /api/v1/admin/alerts/status ---')
res_alert_status = requests.get('http://127.0.0.1:8000/api/v1/admin/alerts/status', headers=headers)
print(f'Status: {res_alert_status.status_code}')
print(json.dumps(res_alert_status.json(), ensure_ascii=False, indent=2))

print('--- LIVE GET /api/v1/public/posts (SORTED BY CREATED_AT DESC) ---')
res_posts = requests.get('http://127.0.0.1:8000/api/v1/public/posts')
posts = res_posts.json()
print(f'Total posts: {len(posts)}')
for p in posts[:3]:
    print('  • ID ' + str(p.get('id')) + ': ' + str(p.get('title')) + ' | ' + str(p.get('created_at')))
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

