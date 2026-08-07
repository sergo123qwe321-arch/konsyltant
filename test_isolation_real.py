import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from rag import ask_consultant

def main():
    print("=== ТЕСТ ИЗОЛЯЦИИ И ЧЕСТНОСТИ ПО НАСТОЯЩИМ ДОКУМЕНТАМ ЯНДЕКС.ДИСКА ===")

    # 1. Александр Морозов - Вопрос про давление
    alex_folder = "disk:/Александр Морозов"
    print(f"\n--- Пациент: Александр Морозов ({alex_folder}) ---")
    alex_prompt = "Какое у меня артериальное давление?"
    print(f"Вопрос: '{alex_prompt}'")
    alex_reply = ask_consultant(alex_prompt, alex_folder)
    print("Ответ ИИ-Консультанта:")
    print(alex_reply)

    # 2. Зоя Космодемьянская - Вопрос про анализы
    zoya_folder = "disk:/Зоя Космодемьянская"
    print(f"\n--- Пациент: Зоя Космодемьянская ({zoya_folder}) ---")
    zoya_prompt = "Что написано в моем заключении о полушариях мозга и гемоглобине?"
    print(f"Вопрос: '{zoya_prompt}'")
    zoya_reply = ask_consultant(zoya_prompt, zoya_folder)
    print("Ответ ИИ-Консультанта:")
    print(zoya_reply)

if __name__ == "__main__":
    main()
