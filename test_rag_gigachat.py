import sys
import os

# Принудительно устанавливаем UTF-8 кодировку вывода в консоль
sys.stdout.reconfigure(encoding='utf-8')

from rag import ask_consultant

def main():
    print("=== Тестирование ИИ-Консультанта на базе GigaChat (Сбер) ===")
    prompt = "Сделай сводку анализов пациента"
    folder_id = "disk:/Павлик Морозов"
    
    print(f"Запрос: '{prompt}'")
    print("Вызов GigaChat API...")
    reply = ask_consultant(prompt, folder_id)
    print("\n--- Ответ ИИ-Консультанта (GigaChat) ---")
    print(reply)
    print("------------------------------------------")

if __name__ == "__main__":
    main()
