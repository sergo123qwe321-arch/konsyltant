import os
import uuid
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_CREDENTIALS") or os.getenv("GIGACHAT_AUTH_KEY", "")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

def get_gigachat_token():
    if not GIGACHAT_AUTH_KEY:
        print("[GIGACHAT ERROR] GIGACHAT_CREDENTIALS / GIGACHAT_AUTH_KEY отсутствует в .env")
        return None

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {GIGACHAT_AUTH_KEY}"
    }
    payload = {
        "scope": GIGACHAT_SCOPE
    }

    try:
        res = requests.post(url, headers=headers, data=payload, verify=False, timeout=15)
        print(f"[GIGACHAT OAUTH LOG] Status: {res.status_code}")
        if res.status_code == 200:
            token = res.json().get("access_token")
            print(f"[GIGACHAT OAUTH SUCCESS] Токен получен!")
            return token
        else:
            print(f"[GIGACHAT OAUTH ERROR] {res.status_code} - {res.text}")
            return None
    except Exception as e:
        print(f"[GIGACHAT OAUTH ERROR] Исключение: {e}")
        return None

def test_chat():
    token = get_gigachat_token()
    if not token:
        return

    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": "Привет! Напиши кратко, кто ты."}
        ],
        "temperature": 0.7
    }

    try:
        res = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        print(f"[GIGACHAT CHAT LOG] Status: {res.status_code}")
        if res.status_code == 200:
            reply = res.json()["choices"][0]["message"]["content"]
            print(f"[GIGACHAT REPLY]: {reply}")
        else:
            print(f"[GIGACHAT ERROR] {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[GIGACHAT ERROR] Исключение: {e}")

if __name__ == "__main__":
    test_chat()
