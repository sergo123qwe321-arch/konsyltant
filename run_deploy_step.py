import os
import sys
import paramiko
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('159.194.232.74', port=22, username='root', password=os.getenv('BEGET_SSH_PASSWORD'), timeout=15)
transport = ssh.get_transport()
if transport:
    transport.set_keepalive(30)

script = """
cd /root/konsyltant
git fetch origin main
git reset --hard origin/main
git rev-parse --short HEAD
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
for line in iter(stdout.readline, ""):
    print(line, end="", flush=True)
ssh.close()
