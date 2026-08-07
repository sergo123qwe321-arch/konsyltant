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

def get_yandex_file_url(file_path):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
    params = {"path": file_path}
    res = requests.get(url, headers=headers, params=params, timeout=15)
    if res.status_code == 200:
        return res.json().get("file")
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

def main():
    print("=== ИНСПЕКЦИЯ ФАЙЛА ТИМУРА РОДРИГЕСА ===")
    
    # 1. Получаем список файлов в папке
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
    params = {"path": "disk:/Тимур Родригес"}
    res = requests.get(url, headers=headers, params=params, timeout=15)
    if res.status_code == 200:
        items = res.json().get("_embedded", {}).get("items", [])
        for item in items:
            fpath = item.get("path")
            fname = item.get("name")
            print(f"Файл: '{fname}' | Path: '{fpath}'")
            down_url = get_yandex_file_url(fpath)
            if down_url:
                c_res = requests.get(down_url, timeout=15)
                if c_res.status_code == 200:
                    text = extract_docx_text(c_res.content)
                    print(f"\nТЕКСТ ИЗ ФАЙЛА '{fname}':\n{text}\n")

if __name__ == "__main__":
    main()
