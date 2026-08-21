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

echo '=== 3. RUN ALL IN-CONTAINER TESTS (39 TESTS) ==='
docker compose exec web python -m unittest test_observability_metrics.py test_etl_diagnostic.py test_yandex_disk_autonomy.py test_sharing_limit.py test_pdf_generation.py test_doctor_summary_api.py test_rate_limiting.py test_db_indexes.py test_e2e_doctor_share.py -v

echo '=== 4. LIVE VERIFICATION OF NEW ENDPOINTS ==='
docker compose exec web python -c "
import requests, json
from security_utils import create_access_token
from rag import get_gigachat_balance

admin_token = create_access_token({'sub': 'admin', 'role': 'ADMIN'})
headers = {'Authorization': f'Bearer {admin_token}'}

print('--- LIVE GIGACHAT OFFICIAL BALANCE CALL ---')
bal = get_gigachat_balance()
print(json.dumps(bal, ensure_ascii=False, indent=2))

print('--- LIVE GET /api/v1/admin/etl/metrics ---')
res_etl = requests.get('http://127.0.0.1:8000/api/v1/admin/etl/metrics', headers=headers)
print(f'Status: {res_etl.status_code}')
print(json.dumps(res_etl.json(), ensure_ascii=False, indent=2))

print('--- LIVE GET /api/v1/admin/llm/usage ---')
res_llm = requests.get('http://127.0.0.1:8000/api/v1/admin/llm/usage', headers=headers)
print(f'Status: {res_llm.status_code}')
print(json.dumps(res_llm.json(), ensure_ascii=False, indent=2))

print('--- LIVE GET /api/v1/admin/diagnose/folder/Дюзгёрен Арон Альп ---')
res_diag = requests.get('http://127.0.0.1:8000/api/v1/admin/diagnose/folder/Дюзгёрен%20Арон%20Альп', headers=headers)
print(f'Status: {res_diag.status_code}')
print(json.dumps(res_diag.json(), ensure_ascii=False, indent=2))
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

