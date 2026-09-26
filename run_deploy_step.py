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
echo '=== 1. DOCKER BUILD WEB ==='
docker compose build web

echo '=== 2. DOCKER UP -D ==='
docker compose up -d
sleep 4

echo '=== 3. DOCKER COMPOSE PS ==='
docker compose ps

echo '=== 4. DOCKER LOGS WEB (TAIL 40) ==='
docker compose logs --tail=40 web
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
