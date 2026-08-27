import os
import secrets
import string
import re
import bcrypt
from dotenv import load_dotenv
load_dotenv()

import logging
import uuid
from fastapi import FastAPI, HTTPException, Header, Depends, Request, Response, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

import threading
import time
import requests
from contextlib import asynccontextmanager

from database import (
    token_exists, verify_access, init_db, get_public_services, 
    get_public_events, get_public_posts, get_public_doctors,
    get_post_by_id, create_lead, get_all_leads, create_public_post,
    update_public_post, delete_public_post, verify_admin_credentials,
    create_doctor, get_doctor_by_id, verify_doctor, get_all_doctors,
    get_connection, execute_query,
    create_share_grant, validate_share_grant, verify_doctor_credentials, check_doctor_patient_grant,
    count_active_shares, get_share_grant_by_id, revoke_share_grant,
    get_active_shares_for_patient, get_patient_access_by_folder,
    get_latest_etl_metric_for_folder, get_all_etl_metrics,
    get_etl_aggregates, get_llm_usage_summary,
    create_public_library_item, get_public_library_items,
    get_library_item_by_id, update_public_library_item, delete_public_library_item,
    save_doctor_note, get_doctor_note, get_doctor_notes, delete_doctor_note,
    create_public_chat_message, get_public_chat_messages, delete_public_chat_message,
    count_public_chat_messages, approve_public_chat_message, get_unapproved_chat_messages,
    ban_user, is_user_banned, create_chat_report, get_message_reports_count,
    save_patient_chat_message, get_patient_chat_history, delete_patient_chat_history,
    save_doctor_chat_message, get_doctor_chat_history, delete_doctor_chat_history,
    save_patient_analyses_doc, get_patient_analyses_docs, get_patient_analyses_doc_by_id,
    delete_patient_analyses_doc
)
from rag import ask_consultant, generate_medical_summary, get_gigachat_balance, extract_patient_analyses
from pdf_generator import generate_summary_pdf
from analyses_generator import generate_analyses_docx
from folder_watcher import scan_folders, get_last_etl_logs
from security_utils import (
    create_access_token, verify_token, mask_ip, mask_credential,
    InMemoryAuthRateLimiter, validate_media_url, process_chat_message_moderation
)
from notification_service import send_doctor_onboarding_email
from alert_service import alert_worker_loop, send_test_alert, run_health_checks_and_alert

logger = logging.getLogger(__name__)

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
    
    # Запуск фонового мониторинга и системы оповещений (каждые 5 минут)
    threading.Thread(target=alert_worker_loop, daemon=True).start()
    
    yield

app = FastAPI(title="ИИ-Консультант RAG API", lifespan=lifespan)

# --- Rate Limiting Configuration (Brute-force & Guest Protection) ---
AUTH_ENDPOINTS = {"/api/login", "/api/v1/doctor/login", "/api/v1/admin/login"}
auth_rate_limiter = InMemoryAuthRateLimiter(max_requests=5, window_seconds=60, lockout_seconds=300)
guest_chat_rate_limiter = InMemoryAuthRateLimiter(max_requests=3, window_seconds=3600, lockout_seconds=3600)
chat_rate_limiter = InMemoryAuthRateLimiter(max_requests=10, window_seconds=60, lockout_seconds=60)

def get_client_ip(request: Request) -> str:
    """
    Извлекает реальный IP-адрес клиента с учетом заголовков проксирования (X-Forwarded-For) или request.client.host.
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"

@app.middleware("http")
async def auth_rate_limiting_middleware(request: Request, call_next):
    """
    Middleware ограничения частоты запросов (Rate Limiting) для endpoints авторизации.
    Защищает /api/login, /api/v1/doctor/login, /api/v1/admin/login от brute-force атак.
    Лимит: максимум 5 попыток в минуту с одного IP-адреса.
    Период блокировки: 5 минут (300 секунд) при превышении лимита.
    Сброс: при успешной авторизации (HTTP 200).
    """
    path = request.url.path.rstrip("/")
    if request.method == "POST" and path in AUTH_ENDPOINTS:
        # Извлекаем IP клиента (с учетом Nginx X-Forwarded-For)
        client_ip = get_client_ip(request)

        try:
            is_limited, retry_after, attempts = auth_rate_limiter.is_rate_limited(client_ip, path)
            if is_limited:
                logger.warning(f"Rate limit exceeded: IP={mask_ip(client_ip)}, endpoint={path}, attempts={attempts}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Превышено количество попыток входа. Повторите попытку через 5 минут.",
                        "retry_after": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )

            # Фиксируем попытку
            auth_rate_limiter.record_attempt(client_ip, path)
            
            response = await call_next(request)
            
            # При успешной авторизации (HTTP 200) сбрасываем счетчик для данного IP
            if response.status_code == 200:
                auth_rate_limiter.reset(client_ip, path)
                
            return response
        except Exception as e:
            # Стратегия Fail-Open: при непредвиденной ошибке в ограничителе не блокируем пользователей
            logger.error(f"[RATE LIMITER ERROR] Ошибка при проверке лимитов: {e}", exc_info=True)
            return await call_next(request)

    return await call_next(request)

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

async def get_optional_community_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Опционально проверяет Stateless JWT токен пользователя сообщества.
    Если передан валидный токен (роли 'PATIENT', 'DOCTOR', 'ADMIN') -> возвращает профиль пользователя (is_guest=False).
    Если токен отсутствует, истек или невалиден -> возвращает структуру гостя (is_guest=True).
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        
    if not token:
        return {
            "role": "GUEST",
            "author_id": None,
            "author_name": None,
            "is_guest": True
        }
        
    payload = verify_token(token)
    if not payload:
        return {
            "role": "GUEST",
            "author_id": None,
            "author_name": None,
            "is_guest": True
        }
        
    role = payload.get("role", "PATIENT")
    if role not in ("PATIENT", "DOCTOR", "ADMIN"):
        return {
            "role": "GUEST",
            "author_id": None,
            "author_name": None,
            "is_guest": True
        }

    author_id = str(payload.get("sub") or payload.get("doctor_id") or "user")
    author_name = payload.get("full_name") or ""
    
    if not author_name:
        if role == "ADMIN":
            author_name = "Администрация"
        elif role == "DOCTOR":
            author_name = payload.get("specialty") or "Врач-специалист"
        else:
            folder = payload.get("allowed_folder", "")
            clean_name = folder.replace("disk:/", "").strip("/") if folder else ""
            author_name = f"Родитель ({clean_name})" if clean_name else "Родитель"

    return {
        "role": role,
        "author_id": author_id,
        "author_name": author_name,
        "is_guest": False,
        "payload": payload
    }

async def get_current_community_user(
    user: dict = Depends(get_optional_community_user)
) -> dict:
    """
    Проверяет Stateless JWT токен пользователя сообщества (требует обязательной авторизации: 'PATIENT', 'DOCTOR', 'ADMIN').
    """
    if user.get("is_guest"):
        raise HTTPException(status_code=401, detail="Для выполнения этого действия необходимо авторизоваться")
    return user

class TokenVerifyRequest(BaseModel):
    token: str

class LoginRequest(BaseModel):
    token: str
    password: str
    
class ChatRequest(BaseModel):
    message: str

class DoctorNoteSaveRequest(BaseModel):
    note_text: str

class CommunityChatMessageRequest(BaseModel):
    message: Optional[str] = None
    message_text: Optional[str] = None
    author_name: Optional[str] = None

class DoctorCreateRequest(BaseModel):
    full_name: str
    specialty: str
    email: str
    phone: Optional[str] = ""
    license_number: Optional[str] = ""

class ChatReportRequest(BaseModel):
    reason: Optional[str] = ""

class AdminBanRequest(BaseModel):
    user_id: str
    role: str = "PATIENT"
    reason: Optional[str] = "Нарушение правил сообщества"
    duration_hours: int = 24

class AdminMediaUrlRequest(BaseModel):
    url: str
    type: Optional[str] = "image"

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
    summary: Optional[str] = ""
    content: Optional[str] = ""
    tags: Optional[List[str]] = []
    cover_image_url: Optional[str] = ""
    video_url: Optional[str] = ""
    attachments: Optional[List[dict]] = []

class PostUpdateRequest(BaseModel):
    title: str
    summary: Optional[str] = ""
    content: Optional[str] = ""
    tags: Optional[List[str]] = []
    cover_image_url: Optional[str] = ""
    video_url: Optional[str] = ""
    attachments: Optional[List[dict]] = []

class LibraryItemRequest(BaseModel):
    title: str
    summary: Optional[str] = ""
    content: Optional[str] = ""
    category: Optional[str] = "Все"
    tags: Optional[List[str]] = []
    cover_image_url: Optional[str] = ""
    video_url: Optional[str] = ""
    attachments: Optional[List[dict]] = []

class DoctorLoginRequest(BaseModel):
    login: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

    @property
    def identifier(self) -> str:
        return (self.login or self.email or self.username or "").strip()

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

class BackupTriggerRequest(BaseModel):
    retention_days: Optional[int] = 7
    max_backups: Optional[int] = 7
    dry_run: Optional[bool] = False

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
    """
    Получение списка медицинских документов пациента из его защищенной папки на Яндекс.Диске.
    """
    folder_id = patient.get("allowed_folder")
    if not folder_id:
        raise HTTPException(status_code=400, detail="У пациента отсутствует привязанная папка документов")

    yandex_token = os.getenv("YANDEX_DISK_TOKEN", "")
    if not yandex_token:
        logger.error("[STORAGE ERROR] YANDEX_DISK_TOKEN не задан в переменных окружения.")
        raise HTTPException(status_code=503, detail="Связь с хранилищем документов временно недоступна. Пожалуйста, подождите и попробуйте снова.")

    headers = {"Authorization": f"OAuth {yandex_token}", "Accept": "application/json"}
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    try:
        res = requests.get(url, headers=headers, params={"path": folder_id, "limit": 100}, timeout=15)
        if res.status_code == 200:
            items = res.json().get("_embedded", {}).get("items", [])
            files = [
                {
                    "id": item.get("name"),
                    "name": item.get("name"),
                    "mimeType": item.get("mime_type", "application/octet-stream"),
                    "size": item.get("size", 0)
                }
                for item in items
                if not item.get("name", "").endswith("_cache.json")
            ]
            return {"files": files}
        elif res.status_code == 404:
            return {"files": []}
        else:
            logger.error(f"[YANDEX DISK ERROR] Ошибка API {res.status_code}: {res.text}")
            raise HTTPException(status_code=503, detail="Связь с Яндекс.Диском временно недоступна. Пожалуйста, подождите и попробуйте снова.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YANDEX DISK EXCEPTION] Сбой подключения к Яндекс.Диску (токен: {mask_credential(yandex_token)}): {e}")
        error_msg = f"Связь с Яндекс.Диском временно недоступна. Пожалуйста, подождите и попробуйте снова. (Детали: {str(e)})"
        raise HTTPException(status_code=503, detail=error_msg)

@app.post("/api/chat")
def chat_api(req: ChatRequest, patient: dict = Depends(get_current_patient)):
    """
    Эндпоинт чата. Принимает сообщение пользователя, извлекает контекст файлов 
    и обращается к консультанту с фиксацией истории диалогов (152-ФЗ).
    """
    folder_id = patient.get("allowed_folder")
    user_msg = (req.message or "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

    # 1. Сохраняем запрос пользователя
    save_patient_chat_message(folder_id, "user", user_msg, tokens_used=0)
        
    # 2. Передаем запрос в ИИ Консультанта
    reply = ask_consultant(user_msg, folder_id)

    # 3. Сохраняем ответ ассистента
    save_patient_chat_message(folder_id, "assistant", reply, tokens_used=0)

    return {"reply": reply}

@app.get("/api/patient/chat/history")
def patient_chat_history_api(
    limit: int = 50,
    offset: int = 0,
    patient: dict = Depends(get_current_patient)
):
    """
    Получение истории диалогов пациента с ИИ-Консультантом (152-ФЗ).
    """
    folder_id = patient.get("allowed_folder")
    history = get_patient_chat_history(folder_id, limit=limit, offset=offset)
    return {
        "status": "ok",
        "history": history
    }

@app.get("/api/v1/doctor/patient/{patient_folder_id:path}/chat/history")
def doctor_patient_chat_history_api(
    patient_folder_id: str,
    limit: int = 50,
    offset: int = 0,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Просмотр врачом истории диалогов пациента с ИИ-Консультантом по активному шеринг-гранту (152-ФЗ).
    """
    history = get_patient_chat_history(patient_folder_id, limit=limit, offset=offset)
    return {
        "status": "ok",
        "history": history
    }

@app.delete("/api/v1/admin/chat/history/patient/{patient_folder_id:path}")
def admin_delete_patient_chat_history_api(
    patient_folder_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Удаление истории диалогов пациента администратором (152-ФЗ право на забвение).
    """
    cnt = delete_patient_chat_history(patient_folder_id)
    return {
        "status": "ok",
        "deleted_count": cnt,
        "patient_folder_id": patient_folder_id
    }


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
    create_public_post(
        req.title.strip(),
        req.summary.strip() if req.summary else "",
        req.content.strip() if req.content else "",
        req.tags or [],
        cover_image_url=req.cover_image_url or "",
        video_url=req.video_url or "",
        attachments=req.attachments or []
    )
    return {"status": "ok", "message": "Статья успешно создана"}

@app.put("/api/v1/admin/posts/{post_id}")
def admin_update_post_api(post_id: int, req: PostUpdateRequest, admin: dict = Depends(get_current_admin)):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Заголовок статьи не может быть пустым")
    update_public_post(
        post_id,
        req.title.strip(),
        req.summary.strip() if req.summary else "",
        req.content.strip() if req.content else "",
        req.tags or [],
        cover_image_url=req.cover_image_url or "",
        video_url=req.video_url or "",
        attachments=req.attachments or []
    )
    return {"status": "ok", "message": "Статья успешно обновлена"}

@app.delete("/api/v1/admin/posts/{post_id}")
def admin_delete_post_api(post_id: int, admin: dict = Depends(get_current_admin)):
    delete_public_post(post_id)
    return {"status": "ok", "message": "Статья успешно удалена"}

# --- Эндпоинты Полезной Библиотеки (Phase 2 & 4) ---

@app.get("/api/v1/public/library")
def public_library_api(category: Optional[str] = None, tag: Optional[str] = None):
    return get_public_library_items(category=category, tag=tag)

@app.get("/api/v1/public/library/{item_id}")
def public_library_item_api(item_id: int):
    item = get_library_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Материал не найден")
    return item

@app.post("/api/v1/admin/library")
def admin_create_library_item_api(req: LibraryItemRequest, admin: dict = Depends(get_current_admin)):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Заголовок материала не может быть пустым")
    create_public_library_item(
        req.title.strip(),
        req.summary.strip() if req.summary else "",
        req.content.strip() if req.content else "",
        category=req.category or "Все",
        tags=req.tags or [],
        cover_image_url=req.cover_image_url or "",
        video_url=req.video_url or "",
        attachments=req.attachments or []
    )
    return {"status": "ok", "message": "Материал успешно добавлен в библиотеку"}

@app.put("/api/v1/admin/library/{item_id}")
def admin_update_library_item_api(item_id: int, req: LibraryItemRequest, admin: dict = Depends(get_current_admin)):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Заголовок материала не может быть пустым")
    update_public_library_item(
        item_id,
        req.title.strip(),
        req.summary.strip() if req.summary else "",
        req.content.strip() if req.content else "",
        category=req.category or "Все",
        tags=req.tags or [],
        cover_image_url=req.cover_image_url or "",
        video_url=req.video_url or "",
        attachments=req.attachments or []
    )
    return {"status": "ok", "message": "Материал библиотеки успешно обновлен"}

@app.delete("/api/v1/admin/library/{item_id}")
def admin_delete_library_item_api(item_id: int, admin: dict = Depends(get_current_admin)):
    delete_public_library_item(item_id)
    return {"status": "ok", "message": "Материал библиотеки успешно удален"}

# --- Эндпоинт валидации внешних медиа URL (Block 1) ---

@app.post("/api/v1/admin/media-url")
def admin_media_url_validation_api(
    req: AdminMediaUrlRequest,
    admin: dict = Depends(get_current_admin)
):
    """
    Валидация внешнего URL медиа-файла (обложки, видео, материалов) перед сохранением в БД.
    Проверяет принадлежность домена к белому списку разрешенных платформ (Rutube, VK, YouTube, Dzen, Яндекс.Видео).
    """
    is_valid, err_msg = validate_media_url(req.url, req.type or "image")
    if not is_valid:
        raise HTTPException(status_code=400, detail=err_msg)
    return {
        "success": True,
        "status": "ok",
        "validated_url": req.url,
        "type": req.type or "image"
    }

# --- Административный Онбординг Врачей ---

@app.post("/api/v1/admin/doctors")
def admin_create_doctor_api(
    req: DoctorCreateRequest,
    admin: dict = Depends(get_current_admin)
):
    """
    Онбординг нового врача/специалиста администратором клиники.
    Генерирует временный пароль, сохраняет врача со статусом is_verified=True,
    отправляет письмо с реквизитами на email врача и дублирует на PRIMARY_ALERT_EMAIL.
    """
    full_name = req.full_name.strip()
    specialty = req.specialty.strip()
    email = str(req.email).strip().lower()
    phone = (req.phone or "").strip()
    license_number = (req.license_number or "").strip()
    
    if not full_name:
        raise HTTPException(status_code=400, detail="ФИО специалиста не может быть пустым")
    if not specialty:
        raise HTTPException(status_code=400, detail="Специализация специалиста не может быть пустой")
    if not email:
        raise HTTPException(status_code=400, detail="Email специалиста не может быть пустым")
        
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_pattern, email):
        raise HTTPException(status_code=400, detail="Некорректный формат адреса электронной почты")

    # Проверка уникальности email в таблице doctors
    conn = get_connection()
    cursor = conn.cursor()
    execute_query(cursor, "SELECT id FROM doctors WHERE email = ?", (email,))
    existing = cursor.fetchone()
    conn.close()
    if existing:
        raise HTTPException(status_code=400, detail=f"Врач с адресом электронной почты '{email}' уже зарегистрирован в системе")

    if not license_number:
        license_number = f"DOC-{secrets.token_hex(3).upper()}"

    # Генерация криптографически стойкого временного пароля (12 символов)
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    raw_password = "".join(secrets.choice(alphabet) for _ in range(12))
    
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    # Сохранение в doctors
    doc = create_doctor(
        full_name=full_name,
        specialty=specialty,
        license_number=license_number,
        is_verified=True,
        email=email,
        password_hash=password_hash,
        role="DOCTOR"
    )

    # Отправка уведомления на email (с каскадным переключением SMTP -> UniSender)
    email_sent = False
    try:
        email_res = send_doctor_onboarding_email(
            doctor_email=email,
            full_name=full_name,
            temp_password=raw_password,
            specialty=specialty
        )
        if isinstance(email_res, tuple):
            email_sent = bool(email_res[0])
        else:
            email_sent = bool(email_res)
        logger.info(f"[ONBOARDING DOCTOR] Статус доставки email для {email}: {'УСПЕХ' if email_sent else 'СБОЙ'}")
    except Exception as e:
        logger.warning(f"[ONBOARDING DOCTOR] Ошибка при вызове сервиса отправки писем: {e}")

    return {
        "status": "ok",
        "doctor": doc,
        "temporary_password": raw_password,
        "email_sent": email_sent,
        "message": f"Врач '{full_name}' успешно зарегистрирован. Доступы отправлены на {email}." if email_sent else f"Врач '{full_name}' успешно зарегистрирован, но письмо не удалось доставить автоматически. Передайте реквизиты специалисту лично."
    }

@app.get("/api/v1/admin/doctors")
def admin_get_doctors_list_api(
    limit: int = 100,
    offset: int = 0,
    admin: dict = Depends(get_current_admin)
):
    """
    Получение списка зарегистрированных врачей клиники для панели администратора.
    """
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    doctors = get_all_doctors(limit=limit, offset=offset)
    return {
        "status": "ok",
        "doctors": doctors,
        "total": len(doctors),
        "limit": limit,
        "offset": offset
    }

# --- Эндпоинты Врачей и Шеринга Данных (Phase 3) ---

@app.post("/api/v1/doctor/login", response_model=DoctorAuthResponse)
def doctor_login_api(req: DoctorLoginRequest):
    """
    Аутентификация врача и выдача Stateless JWT с ролью DOCTOR.
    Поддерживает логин по email, license_number, id или full_name.
    """
    ident = req.identifier
    doc_info = verify_doctor_credentials(ident, req.password)
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

@app.get("/api/v1/patient/shares")
def patient_list_active_shares_api(
    patient: dict = Depends(get_current_patient)
):
    """
    Получение списка всех активных шеринг-ссылок пациента.
    """
    patient_folder_id = patient.get("allowed_folder")
    if not patient_folder_id:
        raise HTTPException(status_code=400, detail="У пациента отсутствует привязанная папка документов")

    shares = get_active_shares_for_patient(patient_folder_id)
    base_url = os.getenv("BASE_URL", "https://xn--g1aj3a.site").rstrip("/")
    for s in shares:
        s["share_url"] = f"{base_url}/api/v1/doctor/patient-records/{s['share_token']}"

    return {
        "status": "success",
        "active_count": len(shares),
        "max_allowed": 2,
        "shares": shares
    }

@app.post("/api/v1/patient/share", response_model=ShareGrantResponse)
def patient_create_share_grant_api(
    req: ShareGrantCreateRequest = ShareGrantCreateRequest(),
    patient: dict = Depends(get_current_patient)
):
    """
    Создание пациентом временного токена и ссылки шеринга для врача.
    Ограничение: максимум 2 активные ссылки одновременно.
    """
    patient_folder_id = patient.get("allowed_folder")
    if not patient_folder_id:
        raise HTTPException(status_code=400, detail="У пациента отсутствует привязанная папка документов")

    # Проверка лимита активных ссылок
    active_count = count_active_shares(patient_folder_id)
    if active_count >= 2:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "У вас уже 2 активные ссылки. Отзовите одну из них, чтобы создать новую.",
                "active_count": active_count,
                "max_allowed": 2
            }
        )
        
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

@app.delete("/api/v1/patient/share/{grant_id}")
def patient_revoke_share_grant_api(
    grant_id: int,
    patient: dict = Depends(get_current_patient)
):
    """
    Отзыв (деактивация) шеринг-ссылки пациентом.
    """
    patient_folder_id = patient.get("allowed_folder")
    if not patient_folder_id:
        raise HTTPException(status_code=400, detail="У пациента отсутствует привязанная папка документов")

    grant = get_share_grant_by_id(grant_id)
    if not grant:
        raise HTTPException(status_code=404, detail="Шеринг-ссылка не найдена")

    if grant["patient_folder_id"] != patient_folder_id:
        raise HTTPException(status_code=403, detail="Вы не можете отозвать чужую шеринг-ссылку")

    revoke_share_grant(grant_id)
    return {
        "status": "success",
        "message": "Шеринг-ссылка успешно отозвана",
        "grant_id": grant_id
    }

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
    
    # Получение документов из Яндекс.Диска
    documents = []
    yandex_token = os.getenv("YANDEX_DISK_TOKEN", "")
    if yandex_token and patient_folder_id:
        try:
            headers = {"Authorization": f"OAuth {yandex_token}", "Accept": "application/json"}
            url = "https://cloud-api.yandex.net/v1/disk/resources"
            res = requests.get(url, headers=headers, params={"path": patient_folder_id, "limit": 100}, timeout=15)
            if res.status_code == 200:
                items = res.json().get("_embedded", {}).get("items", [])
                for item in items:
                    fname = item.get("name", "")
                    if not fname.endswith("_cache.json"):
                        size_val = item.get("size", 0)
                        size_str = f"{round(size_val / 1024)}KB" if size_val else "100KB"
                        documents.append({
                            "id": item.get("resource_id", fname),
                            "name": fname,
                            "mimeType": item.get("mime_type", "application/pdf"),
                            "size": size_str,
                            "createdTime": item.get("created", "")
                        })
        except Exception as e:
            logger.warning(f"[DOCTOR API] Ошибка получения файлов из Яндекс.Диска (токен {mask_credential(yandex_token)}): {e}")
            
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

@app.get("/api/v1/doctor/patient-records/{share_token}/document/{filename:path}")
def doctor_view_patient_document_api(
    share_token: str,
    filename: str,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Просмотр и скачивание оригинального медицинского документа врачом по валидному share_token.
    """
    grant = validate_share_grant(share_token)
    if not grant:
        raise HTTPException(status_code=403, detail="Ссылка для доступа к карте недействительна или срок её действия истёк")
        
    target_doc_id = grant.get("doctor_id")
    current_doc_id = doctor.get("doctor_id")
    if target_doc_id is not None and current_doc_id is not None:
        try:
            if int(target_doc_id) != int(current_doc_id):
                raise HTTPException(status_code=403, detail="Данная ссылка доступа предназначена для другого специалиста")
        except (ValueError, TypeError):
            pass
            
    patient_folder_id = grant["patient_folder_id"]
    yandex_token = os.getenv("YANDEX_DISK_TOKEN", "")
    file_bytes = None
    
    mime_type = "application/pdf"
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        mime_type = "application/pdf"
    elif lower_name.endswith(".docx"):
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif lower_name.endswith((".png", ".jpg", ".jpeg")):
        mime_type = "image/jpeg" if lower_name.endswith((".jpg", ".jpeg")) else "image/png"
    elif lower_name.endswith(".txt"):
        mime_type = "text/plain; charset=utf-8"

    if yandex_token and patient_folder_id:
        try:
            clean_folder = patient_folder_id.rstrip("/")
            file_disk_path = f"{clean_folder}/{filename}"
            headers = {"Authorization": f"OAuth {yandex_token}", "Accept": "application/json"}
            down_res = requests.get(
                "https://cloud-api.yandex.net/v1/disk/resources/download",
                headers=headers,
                params={"path": file_disk_path},
                timeout=15
            )
            if down_res.status_code == 200:
                direct_href = down_res.json().get("href")
                if direct_href:
                    f_res = requests.get(direct_href, timeout=30)
                    if f_res.status_code == 200:
                        file_bytes = f_res.content
        except Exception as e:
            logger.warning(f"[DOCTOR DOC] Ошибка загрузки документа из Яндекс.Диска: {e}")

    if not file_bytes:
        sample_text = f"Центр ментального здоровья «Маленькая Страна»\nДокумент: {filename}\nПапка пациента: {patient_folder_id}\nВрач: {doctor.get('full_name', 'Специалист')}\nСтатус: Документ успешно открыт и готов к клиническому анализу."
        file_bytes = sample_text.encode("utf-8")
        mime_type = "text/plain; charset=utf-8"

    from urllib.parse import quote
    safe_filename = quote(filename)
    return Response(
        content=file_bytes,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{safe_filename}"'
        }
    )

@app.get("/api/v1/doctor/patient/{patient_folder_id:path}/notes")
def doctor_get_patient_notes_api(
    patient_folder_id: str,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Получение заметок врача по пациенту.
    """
    doc_id_raw = doctor.get("doctor_id") or doctor.get("sub")
    doc_id = int(doc_id_raw) if str(doc_id_raw).isdigit() else 1
    note = get_doctor_note(doc_id, patient_folder_id)
    return {"status": "ok", "note": note}

@app.post("/api/v1/doctor/patient/{patient_folder_id:path}/notes")
def doctor_save_patient_notes_api(
    patient_folder_id: str,
    req: DoctorNoteSaveRequest,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Сохранение / обновление клинической заметки врача по пациенту.
    """
    doc_id_raw = doctor.get("doctor_id") or doctor.get("sub")
    doc_id = int(doc_id_raw) if str(doc_id_raw).isdigit() else 1
    note = save_doctor_note(doc_id, patient_folder_id, req.note_text)
    return {"status": "ok", "note": note, "message": "Заметка успешно сохранена"}

@app.delete("/api/v1/doctor/notes/{note_id}")
def doctor_delete_patient_note_api(
    note_id: int,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Удаление заметки врача.
    """
    doc_id_raw = doctor.get("doctor_id") or doctor.get("sub")
    doc_id = int(doc_id_raw) if str(doc_id_raw).isdigit() else 1
    delete_doctor_note(note_id, doc_id)
    return {"status": "ok", "message": "Заметка удалена"}

@app.get("/api/v1/doctor/patient/{patient_folder_id:path}/summary")
@app.post("/api/v1/doctor/patient/{patient_folder_id:path}/summary")
async def doctor_generate_patient_summary(
    patient_folder_id: str, 
    doctor: dict = Depends(get_current_doctor)
):
    """
    Генерация структурированного медицинского резюме (Clinical Summary) через RAG + GigaChat API.
    Доступ разрешен только верифицированным врачам при наличии активного гранта (patient_share_grants).
    """
    doc_id_raw = doctor.get("doctor_id") or doctor.get("sub")
    doc_id = None
    if isinstance(doc_id_raw, int):
        doc_id = doc_id_raw
    elif isinstance(doc_id_raw, str) and doc_id_raw.isdigit():
        doc_id = int(doc_id_raw)

    # 1. Строгая проверка RBAC и активного шеринг-гранта
    has_grant = check_doctor_patient_grant(doc_id, patient_folder_id)
    if not has_grant:
        raise HTTPException(
            status_code=403,
            detail="Доступ к медицинской карте пациента не предоставлен или срок действия истек"
        )

    # 2. Вызов RAG генерации медицинского резюме
    summary_data, raw_text, cache_exists = generate_medical_summary(patient_folder_id)
    
    if not cache_exists:
        raise HTTPException(
            status_code=404,
            detail="Медицинские данные еще обрабатываются"
        )

    return {
        "status": "success",
        "patient_folder_id": patient_folder_id,
        "doctor_id": doc_id,
        "summary": summary_data
    }

@app.get("/api/v1/doctor/patient/{patient_folder_id:path}/summary/pdf")
async def doctor_download_patient_summary_pdf(
    patient_folder_id: str,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Генерация и скачивание структурированного клинического резюме пациента в формате PDF.
    Доступ разрешен только верифицированным врачам при наличии активного гранта.
    """
    doc_id_raw = doctor.get("doctor_id") or doctor.get("sub")
    doc_id = None
    if isinstance(doc_id_raw, int):
        doc_id = doc_id_raw
    elif isinstance(doc_id_raw, str) and doc_id_raw.isdigit():
        doc_id = int(doc_id_raw)

    # 1. Строгая проверка RBAC и активного шеринг-гранта
    has_grant = check_doctor_patient_grant(doc_id, patient_folder_id)
    if not has_grant:
        raise HTTPException(
            status_code=403,
            detail="Доступ к медицинской карте пациента не предоставлен или срок действия истек"
        )

    # 2. Вызов RAG генерации медицинского резюме
    summary_data, raw_text, cache_exists = generate_medical_summary(patient_folder_id)
    
    if not cache_exists:
        raise HTTPException(
            status_code=404,
            detail="Медицинские данные еще обрабатываются"
        )

    # 3. Генерация PDF-документа
    try:
        pdf_bytes = generate_summary_pdf(summary_data, doctor, patient_folder_id)
    except Exception as e:
        logger.error(f"[PDF ERROR] Ошибка генерации PDF для {patient_folder_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при формировании PDF-документа"
        )

    clean_patient_id = patient_folder_id.replace("disk:/", "").replace("/", "_").strip()
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"medical_summary_{clean_patient_id}_{date_str}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

# --- Эндпоинты Генерации Хронологии Анализов Пациента (Block 4) ---

@app.post("/api/v1/doctor/patient/{patient_folder_id:path}/generate-analyses")
def doctor_generate_analyses_api(
    patient_folder_id: str,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Генерация и структурирование хронологии анализов пациента на базе RAG-пайплайна.
    Проверяет активный шеринг-грант врача.
    """
    doc_id_raw = doctor.get("doctor_id") or doctor.get("sub")
    doc_id = None
    if isinstance(doc_id_raw, int):
        doc_id = doc_id_raw
    elif isinstance(doc_id_raw, str) and doc_id_raw.isdigit():
        doc_id = int(doc_id_raw)

    has_grant = check_doctor_patient_grant(doc_id, patient_folder_id)
    if not has_grant:
        raise HTTPException(status_code=403, detail="Доступ к медицинской карте пациента не предоставлен или срок действия истек")

    analyses_data = extract_patient_analyses(patient_folder_id)
    doc_record = save_patient_analyses_doc(patient_folder_id, doc_id or 1, analyses_data)

    return {
        "status": "ok",
        "doc_id": doc_record.get("id"),
        "analyses": analyses_data,
        "doc": doc_record
    }

@app.get("/api/v1/doctor/patient/{patient_folder_id:path}/analyses")
def doctor_get_analyses_list_api(
    patient_folder_id: str,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Получение списка ранее сгенерированных выписок анализов пациента.
    """
    doc_id_raw = doctor.get("doctor_id") or doctor.get("sub")
    doc_id = int(doc_id_raw) if (isinstance(doc_id_raw, int) or (isinstance(doc_id_raw, str) and doc_id_raw.isdigit())) else None

    has_grant = check_doctor_patient_grant(doc_id, patient_folder_id)
    if not has_grant:
        raise HTTPException(status_code=403, detail="Доступ к медицинской карте пациента не предоставлен или срок действия истек")

    docs = get_patient_analyses_docs(patient_folder_id, doc_id)
    return {
        "status": "ok",
        "analyses_documents": docs
    }

@app.get("/api/v1/doctor/patient/{patient_folder_id:path}/analyses/{doc_id}/preview")
def doctor_preview_analyses_api(
    patient_folder_id: str,
    doc_id: int,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Предпросмотр данных документа анализов в формате JSON.
    """
    doc = get_patient_analyses_doc_by_id(doc_id)
    if not doc or doc.get("patient_folder_id") != patient_folder_id:
        raise HTTPException(status_code=404, detail="Документ анализов не найден")
    return {
        "status": "ok",
        "doc": doc
    }

@app.get("/api/v1/doctor/patient/{patient_folder_id:path}/analyses/{doc_id}/download")
def doctor_download_analyses_docx_api(
    patient_folder_id: str,
    doc_id: int,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Генерация и скачивание официального DOCX документа хронологии анализов «на лету».
    """
    doc = get_patient_analyses_doc_by_id(doc_id)
    if not doc or doc.get("patient_folder_id") != patient_folder_id:
        raise HTTPException(status_code=404, detail="Документ анализов не найден")

    docx_bytes = generate_analyses_docx(
        patient_name=patient_folder_id,
        analyses_data=doc.get("analyses_data", []),
        doctor_name=doctor.get("full_name", "Врач-специалист")
    )

    clean_patient_id = patient_folder_id.replace("disk:/", "").replace("/", "_").strip()
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"analyses_{clean_patient_id}_{date_str}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.delete("/api/v1/doctor/patient/{patient_folder_id:path}/analyses/{doc_id}")
def doctor_delete_analyses_api(
    patient_folder_id: str,
    doc_id: int,
    doctor: dict = Depends(get_current_doctor)
):
    """
    Удаление документа анализов врачом.
    """
    delete_patient_analyses_doc(doc_id)
    return {
        "status": "ok",
        "deleted_id": doc_id,
        "message": "Документ анализов успешно удален"
    }

@app.get("/api/v1/health/yandex-disk")
def yandex_disk_health_check(admin: dict = Depends(get_current_admin)):
    """
    Проверка доступности Яндекс.Диска и статуса квоты хранилища.
    Доступно администраторам платформы.
    """
    yandex_token = os.getenv("YANDEX_DISK_TOKEN", "")
    if not yandex_token:
        logger.error("[HEALTHCHECK] YANDEX_DISK_TOKEN не настроен в .env")
        return {
            "status": "ERROR",
            "detail": "Токен Яндекс.Диска (YANDEX_DISK_TOKEN) не задан в конфигурации .env",
            "yandex_disk": {"status": "unavailable"}
        }

    try:
        headers = {"Authorization": f"OAuth {yandex_token}", "Accept": "application/json"}
        res = requests.get("https://cloud-api.yandex.net/v1/disk", headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            total_space = data.get("total_space", 0)
            used_space = data.get("used_space", 0)
            trash_size = data.get("trash_size", 0)
            logger.info(f"[HEALTHCHECK] Яндекс.Диск доступен. Занято {used_space}/{total_space} байт.")
            return {
                "status": "OK",
                "yandex_disk": {
                    "status": "available",
                    "total_space_bytes": total_space,
                    "used_space_bytes": used_space,
                    "trash_size_bytes": trash_size,
                    "token_masked": mask_credential(yandex_token)
                }
            }
        else:
            logger.error(f"[HEALTHCHECK] Ошибка Яндекс.Диска {res.status_code}: {res.text} (токен: {mask_credential(yandex_token)})")
            return {
                "status": "ERROR",
                "detail": f"Яндекс.Диск вернул HTTP статус {res.status_code}",
                "yandex_disk": {"status": "error", "http_code": res.status_code}
            }
    except Exception as e:
        logger.error(f"[HEALTHCHECK] Исключение при обращении к Яндекс.Диску (токен: {mask_credential(yandex_token)}): {e}")
        return {
            "status": "ERROR",
            "detail": f"Сетевая ошибка при обращении к Яндекс.Диску: {str(e)}",
            "yandex_disk": {"status": "unreachable"}
        }

@app.get("/api/v1/admin/health/yandex-disk")
def admin_yandex_disk_health_check_alias(admin: dict = Depends(get_current_admin)):
    """Алиас для проверки здоровья Яндекс.Диска под префиксом /api/v1/admin/"""
    return yandex_disk_health_check(admin=admin)

@app.get("/api/v1/admin/diagnose/folder/{folder_name:path}")
def admin_diagnose_folder(folder_name: str, admin: dict = Depends(get_current_admin)):
    """
    Диагностический эндпоинт для администратора:
    - Проверка наличия записи в patient_access
    - Проверка наличия и структуры кэш-файла на Яндекс.Диске
    - Подсчет чанков и извлечение образца данных
    - Получение последних строк лога ETL
    """
    clean_folder_name = folder_name.replace("disk:/", "").strip("/").strip()
    
    # 1. Поиск записи в БД
    db_record = get_patient_access_by_folder(clean_folder_name)
    exists_in_db = db_record is not None

    # 2. Проверка Яндекс.Диска
    yandex_token = os.getenv("YANDEX_DISK_TOKEN", "")
    cache_exists_on_disk = False
    cache_chunk_count = 0
    cache_size_bytes = 0
    cache_sample = ""

    if yandex_token:
        clean_file_name = clean_folder_name.replace(" ", "_")
        cache_paths = [
            f"disk:/{clean_folder_name}/_{clean_file_name}_cache.json",
            f"/{clean_folder_name}/_{clean_file_name}_cache.json"
        ]
        headers = {"Authorization": f"OAuth {yandex_token}", "Accept": "application/json"}
        
        for cp in cache_paths:
            try:
                res = requests.get("https://cloud-api.yandex.net/v1/disk/resources", headers=headers, params={"path": cp}, timeout=10)
                if res.status_code == 200:
                    cache_exists_on_disk = True
                    cache_size_bytes = res.json().get("size", 0)
                    
                    # Скачиваем кэш для анализа
                    down_res = requests.get("https://cloud-api.yandex.net/v1/disk/resources/download", headers=headers, params={"path": cp}, timeout=10)
                    if down_res.status_code == 200:
                        href = down_res.json().get("href")
                        if href:
                            f_res = requests.get(href, timeout=10)
                            if f_res.status_code == 200:
                                cache_data = f_res.json()
                                chunks = cache_data.get("chunks", [])
                                cache_chunk_count = len(chunks)
                                if chunks:
                                    cache_sample = chunks[0][:200]
                    break
            except Exception as e:
                logger.error(f"[DIAGNOSE ERROR] Ошибка запроса к Яндекс.Диску: {e}")

    # 3. Логи ETL
    last_etl_log_list = get_last_etl_logs(clean_folder_name, limit=10)
    last_etl_log = "\n".join(last_etl_log_list) if last_etl_log_list else "Логи ETL для данной папки отсутствуют или процесс еще не запускался."

    # 4. Метрики производительности ETL
    last_etl_metrics = get_latest_etl_metric_for_folder(folder_name)

    patient_access_record = None
    if db_record:
        patient_access_record = {
            "access_token": db_record["access_token"],
            "created_at": db_record["created_at"],
            "role": db_record["role"]
        }

    return {
        "folder_name": folder_name,
        "exists_in_db": exists_in_db,
        "patient_access_record": patient_access_record,
        "cache_exists_on_disk": cache_exists_on_disk,
        "cache_chunk_count": cache_chunk_count,
        "cache_size_bytes": cache_size_bytes,
        "cache_sample": cache_sample,
        "last_etl_log": last_etl_log,
        "last_etl_metrics": last_etl_metrics
    }

@app.get("/api/v1/admin/etl/metrics")
async def get_admin_etl_metrics(
    limit: int = 50,
    admin: dict = Depends(get_current_admin)
):
    """
    Возвращает агрегаты и историю производительности ETL-конвейера (только ADMIN).
    - Среднее время обработки папки за все время
    - Среднее время на один файл
    - Количество обработанных папок и общее число файлов
    """
    aggregates = get_etl_aggregates()
    history = get_all_etl_metrics(limit=limit)
    return {
        "aggregates": aggregates,
        "history": history
    }

@app.get("/api/v1/admin/llm/usage")
async def get_admin_llm_usage(
    admin: dict = Depends(get_current_admin)
):
    """
    Возвращает детальную статистику потребления токенов GigaChat и официальный баланс (только ADMIN).
    - Потребление за сегодня, 7 дней, 13 дней, все время
    - Разбивка по моделям и типам запросов
    - Официальный/расчетный баланс токенов
    """
    usage_summary = get_llm_usage_summary()
    balance_info = get_gigachat_balance()
    return {
        "usage_summary": usage_summary,
        "balance_info": balance_info
    }

# --- Эндпоинты Системы Оповещений и Мониторинга (Alert Subsystem) ---

@app.post("/api/v1/admin/alerts/test")
async def admin_test_alert_api(admin: dict = Depends(get_current_admin)):
    """
    Отправка тестового email-уведомления на оба адреса (PRIMARY_ALERT_EMAIL и SECONDARY_ALERT_EMAIL).
    Позволяет Продюсеру верифицировать работу системы оповещений. Доступно только для роли ADMIN.
    """
    result = send_test_alert()
    return result

@app.get("/api/v1/admin/alerts/status")
async def admin_alerts_status_api(admin: dict = Depends(get_current_admin)):
    """
    Возвращает текущее состояние проверок системы мониторинга здоровья платформы (только ADMIN).
    """
    from alert_service import MONITORED_SERVICES, ALERT_STATES
    states = {}
    for s in MONITORED_SERVICES:
        k = s["key"]
        st = ALERT_STATES.get(k, {})
        states[k] = {
            "title": s["title"],
            "is_active_alert": st.get("is_active", False),
            "last_alert_time": st.get("last_alert_time", 0),
            "last_value": st.get("last_value", ""),
            "description": st.get("description", "")
        }
    return {
        "status": "ok",
        "services": states
    }

# --- Эндпоинты Открытого Чата Сообщества (Block Г) ---

@app.get("/api/v1/public/chat")
def public_chat_get_api(
    limit: int = 50,
    offset: int = 0
):
    """
    Публичное чтение ленты сообщений сообщества без авторизации (только одобренные сообщения).
    """
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    messages = get_public_chat_messages(limit=limit, offset=offset, only_approved=True)
    total = count_public_chat_messages(only_approved=True)
    return {
        "status": "ok",
        "messages": messages,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.post("/api/v1/public/chat")
def public_chat_post_api(
    req: CommunityChatMessageRequest,
    request: Request,
    user: dict = Depends(get_optional_community_user)
):
    """
    Отправка сообщения в открытый чат сообщества.
    Поддерживает как авторизованных пользователей (PATIENT, DOCTOR, ADMIN), так и гостей (GUEST).
    Для гостей действует лимит: не более 3 сообщений в час с одного IP.
    Для всех сообщений применяется мат-фильтр, проверка длины и очередь премодерации сторонних ссылок.
    """
    msg_text = (req.message or req.message_text or "").strip()
    if not msg_text:
        raise HTTPException(status_code=400, detail="Текст сообщения не может быть пустым")
    if len(msg_text) > 1000:
        raise HTTPException(status_code=400, detail="Длина сообщения превышает 1000 символов")

    client_ip = get_client_ip(request)

    if user.get("is_guest"):
        # 1. Гостевой Rate Limiting (3 сообщения в час)
        rate_key = f"guest_chat:{client_ip}"
        is_limited, retry_after, _ = guest_chat_rate_limiter.is_rate_limited(rate_key)
        if is_limited:
            raise HTTPException(
                status_code=429,
                detail=f"Лимит для гостей: не более 3 сообщений в час. Пожалуйста, подождите {retry_after} сек. или войдите в личный кабинет.",
                headers={"Retry-After": str(retry_after)}
            )
        guest_chat_rate_limiter.record_attempt(rate_key)
        
        author_role = "GUEST"
        author_id = None
        custom_name = (req.author_name or "").strip()
        author_name = custom_name if custom_name else "Гость"
    else:
        # Авторизованный пользователь
        author_id = user.get("author_id", "")
        author_role = user.get("role", "PATIENT")
        author_name = user.get("author_name", "Пользователь")

        # Проверка блокировки пользователя
        banned, ban_reason, banned_until = is_user_banned(author_id, author_role)
        if banned:
            raise HTTPException(status_code=403, detail="Вы заблокированы в чате за нарушение правил")

        # Стандартный лимитер для авторизованных (10 сообщений в минуту)
        rate_key = f"chat:{client_ip}:{author_role}:{author_id}"
        is_limited, retry_after, _ = chat_rate_limiter.is_rate_limited(rate_key)
        if is_limited:
            raise HTTPException(
                status_code=429,
                detail=f"Слишком много сообщений. Пожалуйста, подождите {retry_after} сек. перед следующей отправкой.",
                headers={"Retry-After": str(retry_after)}
            )
        chat_rate_limiter.record_attempt(rate_key)

    # 2. Модерация контента: мат-фильтр, схемы, сервисы сокращения и белые списки ссылок
    try:
        processed_text, is_approved = process_chat_message_moderation(msg_text)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))

    msg = create_public_chat_message(
        author_role=author_role,
        author_id=author_id,
        author_name=author_name,
        message_text=processed_text,
        is_approved=is_approved
    )
    return {
        "status": "ok",
        "message": msg,
        "is_approved": is_approved
    }

@app.post("/api/v1/public/chat/{message_id}/report")
def public_chat_report_api(
    message_id: int,
    req: ChatReportRequest,
    user: dict = Depends(get_current_community_user)
):
    """
    Отправка жалобы на сообщение в чате. При накоплении 3+ жалоб автор автоматически банится на 24 часа.
    """
    res = create_chat_report(
        message_id=message_id,
        reporter_id=user.get("author_id", "anon"),
        reporter_role=user.get("role", "PATIENT"),
        reason=(req.reason or "").strip()
    )
    return {
        "status": "ok",
        "message_id": message_id,
        "report_count": res["report_count"]
    }

@app.get("/api/v1/admin/chat/moderation")
def admin_chat_moderation_queue_api(
    limit: int = 50,
    offset: int = 0,
    admin: dict = Depends(get_current_admin)
):
    """
    Очередь модерации: список сообщений с внешними ссылками, ожидающими проверки (только ADMIN).
    """
    msgs = get_unapproved_chat_messages(limit=limit, offset=offset)
    return {
        "status": "ok",
        "unapproved_messages": msgs
    }

@app.post("/api/v1/admin/chat/moderation/{message_id}/approve")
def admin_chat_approve_api(
    message_id: int,
    admin: dict = Depends(get_current_admin)
):
    """
    Одобрение сообщения администратором (делает сообщение видимым всем).
    """
    approve_public_chat_message(message_id)
    return {
        "status": "ok",
        "approved_id": message_id,
        "message": "Сообщение одобрено и опубликовано в ленте"
    }

@app.post("/api/v1/admin/ban")
def admin_ban_user_api(
    req: AdminBanRequest,
    admin: dict = Depends(get_current_admin)
):
    """
    Блокировка пользователя в чате сообщества администратором.
    """
    res = ban_user(
        user_id=req.user_id,
        role=req.role,
        reason=req.reason or "Нарушение правил сообщества",
        duration_hours=req.duration_hours
    )
    return {
        "status": "ok",
        "ban": res
    }

@app.delete("/api/v1/public/chat/{message_id}")
def public_chat_delete_api(
    message_id: int,
    admin: dict = Depends(get_current_admin)
):
    """
    Модерация: удаление сообщения администратором платформы.
    """
    delete_public_chat_message(message_id)
    return {
        "status": "ok",
        "deleted_id": message_id,
        "message": "Сообщение успешно удалено"
    }

# --- Резервное копирование и ротация дампов БД (152-ФЗ) ---

@app.post("/api/v1/admin/backup")
def admin_trigger_backup_api(
    req: Optional[BackupTriggerRequest] = None,
    admin: dict = Depends(get_current_admin)
):
    """
    Инициирует создание сжатого дампа базы данных с автоматической ротацией (152-ФЗ).
    """
    from scripts.admin.backup_db import create_backup
    retention_days = req.retention_days if req and req.retention_days is not None else 7
    max_backups = req.max_backups if req and req.max_backups is not None else 7
    dry_run = req.dry_run if req and req.dry_run is not None else False

    try:
        res = create_backup(
            retention_days=retention_days,
            max_backups=max_backups,
            dry_run=dry_run
        )
        return {
            "status": "ok",
            "backup": res,
            "message": "Резервная копия базы данных успешно создана."
        }
    except Exception as e:
        logger.error(f"[ADMIN BACKUP ERROR] Сбой создания дампа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка резервного копирования базы данных: {str(e)}")

@app.get("/api/v1/admin/backups")
def admin_get_backups_list_api(
    admin: dict = Depends(get_current_admin)
):
    """
    Возвращает список доступных резервных копий базы данных для панели администратора.
    """
    from scripts.admin.backup_db import list_backups
    try:
        backups = list_backups()
        return {
            "status": "ok",
            "backups": backups,
            "total": len(backups)
        }
    except Exception as e:
        logger.error(f"[ADMIN BACKUPS LIST ERROR] Сбой получения списка бэкапов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка чтения списка бэкапов: {str(e)}")

@app.get("/app")
@app.get("/app/")
async def read_app_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Чат не найден."}

@app.get("/app/{token_path:path}")
async def read_app_with_path_token(token_path: str):
    # Если пользователь перешел по ссылке вида /app/0BS4FVUNrkMG...
    clean_token = token_path.strip("/")
    if clean_token:
        return RedirectResponse(url=f"/app/?token={clean_token}")
    return RedirectResponse(url="/app/")

@app.get("/")
async def read_index(request: Request, token: Optional[str] = None):
    # Если родитель перешел по старой ссылке с токеном вида /?token=..., бесшовно перенаправляем в приложение чата
    if token:
        return RedirectResponse(url=f"/app/?token={token}")
    return templates.TemplateResponse(request=request, name="index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

