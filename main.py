import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

import threading
import time
import requests
from contextlib import asynccontextmanager

from database import token_exists, verify_access, init_db, get_public_services, get_public_events, get_public_posts, get_public_doctors
from drive_api import get_drive_service
from rag import ask_consultant
from folder_watcher import scan_folders
from security_utils import create_access_token, verify_token

def keep_awake_loop():
    """Фоновый пинг сервера, чтобы Render не засыпал (раз в 10 минут)"""
    base_url = os.getenv("BASE_URL")
    if not base_url:
        print("[KEEP-AWAKE] BASE_URL не задан, будильник отключен.")
        return
        
    while True:
        time.sleep(600)  # Ждем 10 минут
        try:
            response = requests.get(base_url, timeout=10)
            print(f"[KEEP-AWAKE] Успешный пинг сервера: {response.status_code}")
        except Exception as e:
            print(f"[KEEP-AWAKE ERROR] Ошибка пинга: {e}")

def watcher_loop():
    while True:
        try:
            scan_folders()
        except Exception as e:
            print(f"Ошибка в фоновом потоке folder_watcher: {e}")
        time.sleep(60) # Проверяем новые папки раз в минуту

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Гарантируем, что БД и таблицы созданы до запуска фоновых процессов
    init_db()
    
    thread = threading.Thread(target=watcher_loop, daemon=True)
    thread.start()
    
    awake_thread = threading.Thread(target=keep_awake_loop, daemon=True)
    awake_thread.start()
    
    yield

app = FastAPI(title="ИИ-Консультант RAG API", lifespan=lifespan)

STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory="templates")

# Bearer аутентификация для OpenAPI и FastApi Dependency
security = HTTPBearer(auto_error=False)

async def get_current_patient(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Проверяет Stateless JWT токен из заголовка Authorization (Bearer <token>).
    Возвращает payload с ID пациента ('sub') и 'allowed_folder'.
    Если токен отсутствует, просрочен или невалиден, возвращает HTTP 401 Unauthorized.
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        
    if not token:
        raise HTTPException(status_code=401, detail="Отсутствует токен авторизации")
        
    payload = verify_token(token)
    if not payload or not payload.get("allowed_folder"):
        raise HTTPException(status_code=401, detail="Сессия недействительна или истекла")
        
    return payload

class TokenVerifyRequest(BaseModel):
    token: str

class LoginRequest(BaseModel):
    token: str
    password: str
    
class ChatRequest(BaseModel):
    message: str

@app.post("/api/verify-token")
async def verify_token_api(req: TokenVerifyRequest):
    if token_exists(req.token):
        return {"valid": True}
    raise HTTPException(status_code=404, detail="Токен не найден или недействителен")

@app.post("/api/login")
async def login_api(req: LoginRequest):
    folder_id = verify_access(req.token, req.password)
    if not folder_id:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    
    # Генерация Stateless JWT токена со временем жизни 30 минут
    jwt_token = create_access_token(data={"sub": req.token, "allowed_folder": folder_id})
    
    return {
        "message": "Успешная авторизация",
        "session_token": jwt_token,
        "access_token": jwt_token,
        "token_type": "bearer"
    }

@app.get("/api/patient/files")
async def get_patient_files(patient: dict = Depends(get_current_patient)):
    folder_id = patient.get("allowed_folder")
        
    service = get_drive_service()
    if not service:
        raise HTTPException(status_code=500, detail="Ошибка подключения к Google Drive")
        
    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        return {"files": files}
    except Exception as e:
        # Понятное сообщение для UI при таймаутах (WinError 10060) и сетевых сбоях
        error_msg = f"Связь с Google Drive временно недоступна. Пожалуйста, подождите и попробуйте снова. (Детали: {str(e)})"
        raise HTTPException(status_code=503, detail=error_msg)

@app.post("/api/chat")
def chat_api(req: ChatRequest, patient: dict = Depends(get_current_patient)):
    """
    Эндпоинт чата. Принимает сообщение пользователя, извлекает контекст файлов 
    и обращается к консультанту.
    """
    folder_id = patient.get("allowed_folder")
        
    # Передаем запрос в ИИ Консультанта
    reply = ask_consultant(req.message, folder_id)
    return {"reply": reply}

@app.get("/api/v1/public/services")
def public_services_api():
    return get_public_services()

@app.get("/api/v1/public/doctors")
def public_doctors_api():
    return get_public_doctors()

@app.get("/api/v1/public/posts")
def public_posts_api(tag: Optional[str] = None):
    return get_public_posts(tag)

@app.get("/api/v1/public/events")
def public_events_api():
    return get_public_events()

@app.get("/app/")
async def read_app_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Чат не найден."}

@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
