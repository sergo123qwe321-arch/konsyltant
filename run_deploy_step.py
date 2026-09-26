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

echo '=== 2. CHECK COMMIT HASH ==='
git rev-parse --short HEAD
git log -n 1 --oneline

echo '=== 3. LINT NO TXT LOGS ==='
python3 scripts/lint_no_txt_logs.py

echo '=== 4. CURRENT GIT STATUS ==='
git status
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
