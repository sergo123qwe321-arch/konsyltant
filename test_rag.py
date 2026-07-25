from rag import ask_consultant
import os

def test_rag():
    print("="*50)
    print("Тестирование ИИ-Консультанта (RAG)")
    print("="*50)
    
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        print("[!] OPENROUTER_API_KEY не установлен. Бот вернет сообщение-заглушку об ошибке доступа к ИИ.\n")
    
    # Тот самый ID папки для тестов
    test_folder_id = "1Hs5A-kx0WfoR8vhUX5xX_XqMtVcwgHu6"
    
    print(">>> Вопрос 1: Какая у меня группа крови?")
    reply1 = ask_consultant("Какая у меня группа крови?", test_folder_id)
    print(f"Ответ ИИ:\n{reply1}\n")
    
    print(">>> Вопрос 2: В документах есть результаты МРТ?")
    reply2 = ask_consultant("В документах есть результаты МРТ?", test_folder_id)
    print(f"Ответ ИИ:\n{reply2}\n")
    
    print("ТЕСТ ЗАВЕРШЕН.")

if __name__ == "__main__":
    test_rag()
