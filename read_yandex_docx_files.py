import os
import sys
import io
import zipfile
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN", "")

def download_yandex_file(download_url):
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
    res = requests.get(download_url, headers=headers, timeout=15)
    if res.status_code == 200:
        return res.content
    return None

def extract_docx_text(docx_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(docx_bytes)) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            texts = []
            for elem in tree.iter():
                if elem.tag.endswith('}t') and elem.text:
                    texts.append(elem.text)
            return " ".join(texts)
    except Exception as e:
        return f"Error parsing docx: {e}"

def get_yandex_file_url(file_path):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
    params = {"path": file_path}
    res = requests.get(url, headers=headers, params=params, timeout=15)
    if res.status_code == 200:
        return res.json().get("file")
    return None

def main():
    print("=== ЧТЕНИЕ НАСТОЯЩИХ ТЕКСТОВ ФАЙЛОВ С ЯНДЕКС ДИСКА ===")

    # 1. Александр Морозов
    alex_file_path = "disk:/Александр Морозов/Морозов.docx"
    print(f"\n--- Чтение файла: {alex_file_path} ---")
    alex_url = get_yandex_file_url(alex_file_path)
    if alex_url:
        content = download_yandex_file(alex_url)
        if content:
            text = extract_docx_text(content)
            print(f"ТЕКСТ ДОКУМЕНТА АЛЕКСАНДРА МОРOЗОВА:\n{text}")

    # 2. Зоя Космодемьянская
    zoya_file_path = "disk:/Зоя Космодемьянская/Зоя.docx"
    print(f"\n--- Чтение файла: {zoya_file_path} ---")
    zoya_url = get_yandex_file_url(zoya_file_path)
    if zoya_url:
        content = download_yandex_file(zoya_url)
        if content:
            text = extract_docx_text(content)
            print(f"ТЕКСТ ДОКУМЕНТА ЗОИ КОСМОДЕМЬЯНСКОЙ:\n{text}")

if __name__ == "__main__":
    main()
