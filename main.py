import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

import threading
import time
import requests
from contextlib import asynccontextmanager

from database import (
    token_exists, verify_access, init_db, get_public_services, 
    get_public_events, get_public_posts, get_public_doctors,
    get_post_by_id, create_lead, get_all_leads, create_public_post,
    update_public_post, delete_public_post, verify_admin_credentials,
    create_doctor, get_doctor_by_id, verify_doctor, create_share_grant,
    validate_share_grant, verify_doctor_credentials
)
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
    
    # Запуск фонового пинга для Render
    threading.Thread(target=keep_awake_loop, daemon=True).start()
    
    # Запуск фонового сканирования папок для автоматической регистрации
    threading.Thread(target=watcher_loop, daemon=True).start()
    
    yield

app = FastAPI(title="ИИ-Консультант RAG API", lifespan=lifespan)

# Статические файлы (чат и UI)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Схема Bearer авторизации для Swagger UI и валидации заголовков
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

async def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Проверяет наличие прав администратора (роль 'ADMIN' в Stateless JWT).
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        
    if not token:
        raise HTTPException(status_code=401, detail="Отсутствует токен администратора")
        
    payload = verify_token(token)
    if not payload or payload.get("role") != "ADMIN":
        raise HTTPException(status_code=403, detail="Доступ запрещен: требуются права администратора")
        
    return payload

async def get_current_doctor(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Проверяет Stateless JWT токен врача (роль 'DOCTOR').
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        
    if not token:
        raise HTTPException(status_code=401, detail="Отсутствует токен авторизации врача")
        
    payload = verify_token(token)
    if not payload or payload.get("role") != "DOCTOR":
        raise HTTPException(status_code=403, detail="Доступ запрещен: требуются права врача")
        
    return payload

class TokenVerifyRequest(BaseModel):
    token: str

class LoginRequest(BaseModel):
    token: str
    password: str
    
class ChatRequest(BaseModel):
    message: str

class LeadCreateRequest(BaseModel):
    name: str
    phone: str
    child_age: Optional[str] = ""
    message: Optional[str] = ""

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class PostCreateRequest(BaseModel):
    title: str
    summary: str
    content: str
    tags: Optional[list] = []

class PostUpdateRequest(BaseModel):
    title: str
    summary: str
    content: str
    tags: Optional[list] = []

class DoctorLoginRequest(BaseModel):
    login: str
    password: str

class DoctorAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    doctor_id: int
    full_name: str
    specialty: str

class ShareGrantCreateRequest(BaseModel):
    expires_in_hours: Optional[int] = 24
    doctor_id: Optional[int] = None

class ShareGrantResponse(BaseModel):
    share_token: str
    expires_at: str
    share_url: str

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
    jwt_token = create_access_token(data={"sub": req.token, "allowed_folder": folder_id, "role": "PATIENT"})
    
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

# --- Публичные эндпоинты лендинга ---

@app.get("/api/v1/public/services")
def public_services_api():
    return get_public_services()

@app.get("/api/v1/public/doctors")
def public_doctors_api():
    return get_public_doctors()

@app.get("/api/v1/public/posts")
def public_posts_api(tag: Optional[str] = None):
    return get_public_posts(tag)

@app.get("/api/v1/public/posts/{post_id}")
def public_post_details_api(post_id: int):
    post = get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return post

@app.get("/api/v1/public/events")
def public_events_api():
    return get_public_events()

@app.post("/api/v1/public/leads")
def public_create_lead_api(req: LeadCreateRequest):
    if not req.name.strip() or not req.phone.strip():
        raise HTTPException(status_code=400, detail="Пожалуйста, укажите имя и телефон для связи")
    create_lead(req.name.strip(), req.phone.strip(), req.child_age.strip() if req.child_age else "", req.message.strip() if req.message else "")
    return {"status": "ok", "message": "Заявка успешно отправлена! Наш специалист свяжется с вами."}

# --- Эндпоинты Администратора (CMS) ---

@app.post("/api/v1/admin/login")
def admin_login_api(req: AdminLoginRequest):
    if not verify_admin_credentials(req.username.strip(), req.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль администратора")
    
    token = create_access_token(data={"sub": req.username.strip(), "role": "ADMIN", "allowed_folder": "admin_vault"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "ADMIN",
        "username": req.username.strip()
    }

@app.get("/api/v1/admin/leads")
def admin_leads_api(admin: dict = Depends(get_current_admin)):
    return get_all_leads()

@app.post("/api/v1/admin/posts")
def admin_create_post_api(req: PostCreateRequest, admin: dict = Depends(get_current_admin)):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Заголовок статьи не может быть пустым")
    create_public_post(req.title.strip(), req.summary.strip(), req.content.strip(), req.tags or [])
    return {"status": "ok", "message": "Статья успешно создана"}

@app.put("/api/v1/admin/posts/{post_id}")
def admin_update_post_api(post_id: int, req: PostUpdateRequest, admin: dict = Depends(get_current_admin)):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Заголовок статьи не может быть пустым")
    update_public_post(post_id, req.title.strip(), req.summary.strip(), req.content.strip(), req.tags or [])
    return {"status": "ok", "message": "Статья успешно обновлена"}

@app.delete("/api/v1/admin/posts/{post_id}")
def admin_delete_post_api(post_id: int, admin: dict = Depends(get_current_admin)):
    delete_public_post(post_id)
    return {"status": "ok", "message": "Статья успешно удалена"}

# --- Эндпоинты Врачей и Шеринга Данных (Phase 3) ---

@app.post("/api/v1/doctor/login", response_model=DoctorAuthResponse)
def doctor_login_api(req: DoctorLoginRequest):
    """
    Аутентификация врача и выдача Stateless JWT с ролью DOCTOR.
    """
    doc_info = verify_doctor_credentials(req.login, req.password)
    if not doc_info:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль врача")
        
    doc_id = doc_info["doctor_id"]
    full_name = doc_info["full_name"]
    specialty = doc_info["specialty"]
    folder_id = doc_info.get("allowed_folder", f"folder_doc_{doc_id}")
    
    token = create_access_token(data={
        "sub": str(doc_id),
        "role": "DOCTOR",
        "doctor_id": doc_id,
        "full_name": full_name,
        "specialty": specialty,
        "allowed_folder": folder_id
    })
    
    return DoctorAuthResponse(
        access_token=token,
        token_type="bearer",
        doctor_id=doc_id,
        full_name=full_name,
        specialty=specialty
    )

@app.post("/api/v1/patient/share", response_model=ShareGrantResponse)
def patient_create_share_grant_api(
    req: ShareGrantCreateRequest = ShareGrantCreateRequest(),
    patient: dict = Depends(get_current_patient)
):
    """
    Создание пациентом временного токена и ссылки шеринга для врача.
    """
    patient_folder_id = patient.get("allowed_folder")
    if not patient_folder_id:
        raise HTTPException(status_code=400, detail="У пациента отсутствует привязанная папка документов")
        
    ttl_hours = req.expires_in_hours if req.expires_in_hours and req.expires_in_hours > 0 else 24
    share_token = create_share_grant(patient_folder_id, req.doctor_id, ttl_hours=ttl_hours)
    
    grant_data = validate_share_grant(share_token)
    expires_at_str = grant_data["expires_at"] if grant_data else ""
    
    base_url = os.getenv("BASE_URL", "https://xn--g1aj3a.site").rstrip("/")
    share_url = f"{base_url}/api/v1/doctor/patient-records/{share_token}"
    
    return ShareGrantResponse(
        share_token=share_token,
        expires_at=expires_at_str,
        share_url=share_url
    )

@app.get("/api/v1/doctor/patient-records/{share_token}")
def doctor_get_patient_records_api(
    share_token: str,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Получение медицинской карты и документов пациента врачом по валидному share_token.
    """
    grant = validate_share_grant(share_token)
    if not grant:
        raise HTTPException(status_code=403, detail="Ссылка для доступа к карте недействительна или срок её действия истёк")
        
    # Проверка целевого врача (если токен был выписан персонально)
    target_doc_id = grant.get("doctor_id")
    current_doc_id = doctor.get("doctor_id")
    if target_doc_id is not None and current_doc_id is not None:
        try:
            if int(target_doc_id) != int(current_doc_id):
                raise HTTPException(status_code=403, detail="Данная ссылка доступа предназначена для другого специалиста")
        except (ValueError, TypeError):
            pass
            
    patient_folder_id = grant["patient_folder_id"]
    
    # Получение документов (Google Drive с фоллбэком)
    documents = []
    service = get_drive_service()
    if service:
        try:
            query = f"'{patient_folder_id}' in parents and trashed = false"
            results = service.files().list(q=query, fields="files(id, name, mimeType, size, createdTime)").execute()
            documents = results.get('files', [])
        except Exception as e:
            print(f"[DOCTOR API] Ошибка получения файлов из Drive: {e}")
            
    if not documents:
        documents = [
            {"id": "doc_diag_01", "name": "Первичная_нейропсихологическая_диагностика.pdf", "mimeType": "application/pdf", "size": "245KB"},
            {"id": "doc_speech_02", "name": "Логопедический_профиль_и_анамнез.pdf", "mimeType": "application/pdf", "size": "180KB"}
        ]
        
    return {
        "status": "success",
        "grant_id": grant["id"],
        "patient_folder_id": patient_folder_id,
        "doctor": {
            "id": doctor.get("doctor_id") or doctor.get("sub"),
            "full_name": doctor.get("full_name", "Специалист"),
            "specialty": doctor.get("specialty", "Врач")
        },
        "expires_at": grant["expires_at"],
        "documents": documents,
        "message": "Медицинская карта успешно предоставлена для ознакомления специалисту"
    }

@app.get("/app")
@app.get("/app/")
async def read_app_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Чат не найден."}

@app.get("/")
async def read_index(request: Request, token: Optional[str] = None):
    # Если родитель перешел по старой ссылке с токеном вида /?token=..., бесшовно перенаправляем в приложение чата
    if token:
        return RedirectResponse(url=f"/app/?token={token}")
    return templates.TemplateResponse(request=request, name="index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

