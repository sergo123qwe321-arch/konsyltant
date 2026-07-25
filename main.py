import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import secrets
from typing import Optional

from database import token_exists, verify_access
from drive_api import get_drive_service
from rag import ask_consultant

app = FastAPI(title="ИИ-Консультант RAG API")

STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

SESSIONS = {}

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
    
    session_token = secrets.token_hex(32)
    SESSIONS[session_token] = folder_id
    
    return {"message": "Успешная авторизация", "session_token": session_token}

@app.get("/api/patient/files")
async def get_patient_files(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Отсутствует токен авторизации")
        
    session_token = authorization.split(" ")[1]
    folder_id = SESSIONS.get(session_token)
    
    if not folder_id:
        raise HTTPException(status_code=401, detail="Сессия недействительна или истекла")
        
    service = get_drive_service()
    if not service:
        raise HTTPException(status_code=500, detail="Ошибка подключения к Google Drive")
        
    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении файлов: {str(e)}")

@app.post("/api/chat")
def chat_api(req: ChatRequest, authorization: Optional[str] = Header(None)):
    """
    Эндпоинт чата. Принимает сообщение пользователя, извлекает контекст файлов 
    и обращается к OpenRouter.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Отсутствует токен авторизации")
        
    session_token = authorization.split(" ")[1]
    folder_id = SESSIONS.get(session_token)
    
    if not folder_id:
        raise HTTPException(status_code=401, detail="Сессия недействительна или истекла")
        
    # Передаем запрос в ИИ Консультанта
    reply = ask_consultant(req.message, folder_id)
    return {"reply": reply}

@app.get("/")
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Фронтенд не найден."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
