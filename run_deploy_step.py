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
docker compose exec web python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(); token=os.getenv('YANDEX_DISK_TOKEN'); h={'Authorization': f'OAuth {token}'}; res=requests.get('https://cloud-api.yandex.net/v1/disk/resources/download?path=disk:/Малышкин Даня/допфайлы/001-2.jpg', headers=h).json(); fbytes=requests.get(res['href']).content; from document_parser import parse_document_bytes; txt=parse_document_bytes(fbytes, '001-2.jpg', 'image/jpeg'); print('extracted len:', len(txt)); print('preview:', repr(txt[:300]))"




"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
print(stdout.read().decode('utf-8', errors='replace'))
ssh.close()
