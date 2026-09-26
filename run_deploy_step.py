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
cat << 'EOF' > verify_cache.py
import json
from folder_watcher import download_yandex_file_bytes
from rag import ask_consultant

patient = 'Малышкин Даня'
clean_name = patient.replace(' ', '_')
cache_path = f'disk:/{patient}/_{clean_name}_cache.json'
cache_bytes = download_yandex_file_bytes(cache_path)
data = json.loads(cache_bytes.decode('utf-8'))
files = data.get('files', {})
chunks = data.get('chunks', [])

print('=== ИТОГОВЫЙ СТАТУС КЭША ===')
print(f'Итоговый размер кэша: {len(cache_bytes)} байт ({len(cache_bytes) / 1024:.2f} KB)')
print(f'Общее количество файлов в кэше: {len(files)}')
print(f'Общее количество текстовых чанков: {len(chunks)}')

print('=== РЕЗУЛЬТАТ ПОИСКА ТЕРМИНА «бибуп» ===')
matches = []
for rel_path, f_entry in files.items():
    for c in f_entry.get('chunks', []):
        if 'бибуп' in c.lower():
            matches.append((rel_path, c))

print(f'Найдено совпадений: {len(matches)}')
for rel_path, c in matches:
    print(f'Файл: {rel_path}')
    print('Содержимое чанка:')
    print(c)
    print()

print('=== ОТВЕТ RAG-КОНСУЛЬТАНТА НА ВОПРОС «Что такое бибуп?» ===')
reply = ask_consultant('Что такое бибуп?', patient)
print('Ответ модели:')
print(reply)
EOF

docker compose cp verify_cache.py web:/app/verify_cache.py
docker compose exec -T web python /app/verify_cache.py
rm -f verify_cache.py
"""

stdin, stdout, stderr = ssh.exec_command(script, get_pty=True)
for line in iter(stdout.readline, ""):
    print(line, end="", flush=True)
ssh.close()
