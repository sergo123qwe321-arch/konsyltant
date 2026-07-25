import os
import io
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = 'credentials.json'

def get_drive_service():
    creds = None
    try:
        # 1. Пробуем получить из переменной окружения (для Render.com)
        env_creds = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if env_creds:
            creds_info = json.loads(env_creds)
            creds = service_account.Credentials.from_service_account_info(
                creds_info, scopes=SCOPES)
        # 2. Иначе используем локальный файл (для разработки)
        elif os.path.exists(CREDENTIALS_FILE):
            creds = service_account.Credentials.from_service_account_file(
                CREDENTIALS_FILE, scopes=SCOPES)
        else:
            logger.error("Учетные данные Google не найдены (ни GOOGLE_CREDENTIALS_JSON, ни credentials.json).")
            return None
            
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Ошибка при инициализации Google Drive API: {e}")
        return None

def download_file(file_id: str, mime_type: str) -> bytes:
    """
    Скачивает содержимое файла из Google Drive.
    Для нативных Google-документов использует экспорт в текст.
    """
    service = get_drive_service()
    if not service:
        return b""
    try:
        if "vnd.google-apps" in mime_type:
            if "document" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType='text/plain')
            else:
                # Пропускаем таблицы/презентации
                return b"" 
        else:
            request = service.files().get_media(fileId=file_id)
            
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return fh.getvalue()
    except Exception as e:
        logger.error(f"Ошибка при скачивании файла {file_id}: {e}")
        return b""
