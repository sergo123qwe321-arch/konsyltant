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
import os
print('BASE_URL:', os.getenv('BASE_URL'))
print('DEFAULT_NOTIFICATION_EMAIL:', os.getenv('DEFAULT_NOTIFICATION_EMAIL'))
"
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()

