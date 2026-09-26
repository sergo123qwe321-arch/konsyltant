import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('159.194.232.74', port=22, username='root', password=os.getenv('BEGET_SSH_PASSWORD'), timeout=15)

script = """
cd /root/konsyltant
echo '=== 1. SYNC REPO ==='
git fetch origin main
git reset --hard origin/main

echo '=== 2. BUILD WEB CONTAINER ==='
docker compose build web
docker compose up -d
sleep 3

echo '=== 3. RUN OCR SYNC FOR МАЛЫШКИН ДАНЯ ==='
docker compose exec web python folder_watcher.py --patient "Малышкин Даня"




"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
