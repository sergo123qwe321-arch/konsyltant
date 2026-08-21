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
cat << 'EOF' | docker compose -f /root/konsyltant/docker-compose.yml exec -T web python -
import os, requests, json
from database import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, access_token, gdrive_folder_id, role, created_at FROM patient_access WHERE gdrive_folder_id LIKE '%Дюзгёрен%' ORDER BY created_at DESC;")
row = cursor.fetchone()
print('=== DB RECORD ===')
if row:
    print('ID:', row[0], 'Token:', row[1], 'Folder:', row[2], 'Role:', row[3], 'Created At:', row[4])
conn.close()

token = os.getenv('YANDEX_DISK_TOKEN')
headers = {'Authorization': f'OAuth {token}'}
res = requests.get('https://cloud-api.yandex.net/v1/disk/resources', headers=headers, params={'path': 'disk:/Дюзгёрен Арон Альп', 'limit': 100})
print('=== YANDEX DISK METADATA ===')
if res.status_code == 200:
    data = res.json()
    print('Folder created:', data.get('created'))
    print('Folder modified:', data.get('modified'))
    items = data.get('_embedded', {}).get('items', [])
    print(f'Total items in folder: {len(items)}')
    for it in items:
        if it.get('name').endswith('_cache.json'):
            print('CACHE FILE:', it.get('name'), 'created:', it.get('created'), 'modified:', it.get('modified'), 'size:', it.get('size'))
    if len(items) > 1:
        print('Sample File 1:', items[1].get('name'), 'created:', items[1].get('created'), 'modified:', items[1].get('modified'))
        print('Sample File Last:', items[-1].get('name'), 'created:', items[-1].get('created'), 'modified:', items[-1].get('modified'))
EOF
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

