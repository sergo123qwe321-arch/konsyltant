import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from database import init_db, verify_access
from rag import ask_consultant

def test_tenant_isolation():
    print("=== ТЕСТИРОВАНИЕ ИЗОЛЯЦИИ ДАННЫХ ПАЦИЕНТОВ (MULTI-TENANT ISOLATION) ===")
    init_db()

    # 1. Запрос от имени Зои Космодемьянской
    zoya_folder = "disk:/Зоя Космодемьянская"
    print(f"\n[ТЕСТ 1] Запрос с папкой Зои Космодемьянской: '{zoya_folder}'")
    zoya_prompt = "Как меня зовут и какие анализы сданы?"
    zoya_reply = ask_consultant(zoya_prompt, zoya_folder)
    print("Ответ ИИ-Консультанта для Зои:")
    print(zoya_reply)

    assert "Павлик" not in zoya_reply, "УТЕЧКА ДАННЫХ: В ответе Зои обнаружен Павлик!"
    assert "Павел" not in zoya_reply, "УТЕЧКА ДАННЫХ: В ответе Зои обнаружен Павел!"
    print("\n🟢 [УСПЕХ ИЗОЛЯЦИИ]: Данные Зои Космодемьянской строго изолированы! Нет ни одного упоминания Павлика Морозова.")

    # 2. Запрос от имени Александра Морозова
    alex_folder = "disk:/Александр Морозов"
    print(f"\n[ТЕСТ 2] Запрос с папкой Александра Морозова: '{alex_folder}'")
    alex_reply = ask_consultant("Какое у меня артериальное давление и ритм сердца?", alex_folder)
    print("Ответ ИИ-Консультанта для Александра:")
    print(alex_reply)

    assert "Павлик" not in alex_reply, "УТЕЧКА ДАННЫХ: В ответе Александра обнаружен Павлик!"
    assert "Зоя" not in alex_reply, "УТЕЧКА ДАННЫХ: В ответе Александра обнаружена Зоя!"
    print("\n🟢 [УСПЕХ ИЗОЛЯЦИИ]: Данные Александра Морозова полностью изолированы!")

if __name__ == "__main__":
    test_tenant_isolation()
