import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from rag import ask_consultant

def main():
    print("=== ТЕСТИРОВАНИЕ ИЗОЛЯЦИИ И ДИНАМИЧЕСКОГО ЧТЕНИЯ ДЛЯ ТИМУРА РОДРИГЕСА ===")
    
    timur_folder = "disk:/Тимур Родригес"
    print(f"\nЗапрос под авторизацией папки: '{timur_folder}'")
    prompt = "Сделай подробный разбор моих анализов и заключения врача"
    
    reply = ask_consultant(prompt, timur_folder)
    print("\n--- Ответ ИИ-Консультанта для Тимура Родригеса ---")
    print(reply)
    print("--------------------------------------------------")

    assert "Павлик" not in reply, "ОШИБКА: Обнаружены данные Павлика Морозова!"
    assert "Зоя" not in reply, "ОШИБКА: Обнаружены данные Зои!"
    print("\n🟢 [УСПЕХ ИЗОЛЯЦИИ]: Ответ сгенерирован СТРОГО по документам Тимура Родригеса!")

if __name__ == "__main__":
    main()
