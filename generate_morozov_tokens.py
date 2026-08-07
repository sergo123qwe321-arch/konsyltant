import os
import secrets
import string
from dotenv import load_dotenv
from database import init_db, create_patient_access
from security_utils import mask_credential, mask_url

load_dotenv()

def main():
    init_db()
    
    chars = string.ascii_letters + string.digits + "!@#$"
    
    # 1. Папка "Павлик Морозов"
    passcode_folder = ''.join(secrets.choice(chars) for _ in range(12))
    token_folder = create_patient_access(passcode_folder, "disk:/Павлик Морозов")
    
    # 2. Файл "Морозов Павел...ЭК.pdf"
    passcode_file = ''.join(secrets.choice(chars) for _ in range(12))
    token_file = create_patient_access(passcode_file, "disk:/Морозов Павел...ЭК.pdf")
    
    print("\n=========================================================")
    print("[SECURE ACCESS LOG]")
    print("Folder: Павлик Морозов")
    print(f"URL: {mask_url(f'http://127.0.0.1:8000/?token={token_folder}')}")
    print(f"Passcode: {mask_credential(passcode_folder)}")
    print("=========================================================\n")

if __name__ == "__main__":
    main()
