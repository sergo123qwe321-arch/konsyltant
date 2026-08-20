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
docker compose -f /root/konsyltant/docker-compose.yml exec web python -c "
import requests
res = requests.post('http://127.0.0.1:8000/api/v1/doctor/login', json={'email': 'producer@cmz.site', 'password': 'TestAccess2026!'})
print('Status Code:', res.status_code)
print('Response Body:', res.json())
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

