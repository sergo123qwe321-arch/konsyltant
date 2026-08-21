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

echo '=== 4. RUN ALL IN-CONTAINER TESTS (44 TESTS) ==='
docker compose exec web python -m unittest test_landing_and_admin_ops.py test_observability_metrics.py test_etl_diagnostic.py test_yandex_disk_autonomy.py test_sharing_limit.py test_pdf_generation.py test_doctor_summary_api.py test_rate_limiting.py test_db_indexes.py test_e2e_doctor_share.py -v

echo '=== 5. LIVE VERIFICATION OF ADMIN LOGIN & PUBLIC POSTS ==='
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

print('--- LIVE GET /api/v1/public/posts (SORTED BY CREATED_AT DESC) ---')
res_posts = requests.get('http://127.0.0.1:8000/api/v1/public/posts')
posts = res_posts.json()
print(f'Total posts: {len(posts)}')
for p in posts[:3]:
    print(f'  • ID {p.get(\"id\")}: {p.get(\"title\")} | {p.get(\"created_at\")}')

print('--- LIVE GET /api/v1/admin/etl/metrics WITH PRODUCER TOKEN ---')
res_etl = requests.get('http://127.0.0.1:8000/api/v1/admin/etl/metrics', headers=headers)
print(f'Status: {res_etl.status_code}, Folders processed: {res_etl.json().get(\"aggregates\", {}).get(\"total_folders_processed\")}')
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

