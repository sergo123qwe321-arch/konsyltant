import time
import os
import sys
import json
from dotenv import load_dotenv

# Настройка безопасной кодировки консоли для Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from folder_watcher import sync_patient_folder, download_yandex_file_bytes

def main():
    patient = "Малышкин Даня"
    batch_limit = 50
    iteration = 1

    print(f"=== Запуск непрерывной синхронизации для '{patient}' (batch_limit={batch_limit}) ===")
    
    while True:
        print(f"\n--- Итерация #{iteration} ---")
        remaining = sync_patient_folder(patient_folder=patient, batch_limit=batch_limit)
        print(f"Результат итерации: осталось необработанных файлов: {remaining}")
        
        if remaining <= 0:
            print("\n✅ Все файлы успешно проиндексированы (остаток: 0)!")
            break
            
        iteration += 1
        time.sleep(1.5)

    # Проверка итогового кэша на Яндекс.Диске
    print("\n=== Проверка итогового кэша _Малышкин_Даня_cache.json ===")
    cache_path = f"disk:/{patient}/_{patient.replace(' ', '_')}_cache.json"
    cache_bytes = download_yandex_file_bytes(cache_path)
    if not cache_bytes:
        print(f"❌ Ошибка скачивания кэша '{cache_path}'")
        return

    data = json.loads(cache_bytes.decode('utf-8'))
    files = data.get("files", {})
    chunks = data.get("chunks", [])
    print(f"Итоговый размер кэша: {len(cache_bytes)} байт ({len(cache_bytes) / 1024:.2f} KB)")
    print(f"Общее количество файлов в кэше: {len(files)} (ожидается 594)")
    print(f"Общее количество чанков в кэше: {len(chunks)}")

    # Поиск слова «бибуп» по всем чанкам и файлам
    matches = []
    for rel_path, f_entry in files.items():
        for chunk in f_entry.get("chunks", []):
            if "бибуп" in chunk.lower():
                matches.append((rel_path, chunk))

    print(f"\n=== Результат поиска термина «бибуп» ===")
    if matches:
        print(f"Найдено совпадений: {len(matches)}")
        for rel_path, chunk in matches:
            print(f"Файл: '{rel_path}'\nФрагмент:\n{chunk[:300]}...\n")
    else:
        print("Совпадений со словом «бибуп» не найдено ни в одном из файлов кэша (0 совпадений).")

    # Проверка ответа RAG-консультанта через ask_consultant
    print(f"\n=== Проверка ответа RAG-консультанта на вопрос «Что такое бибуп?» ===")
    try:
        from rag import ask_consultant
        reply = ask_consultant("Что такое бибуп?", patient)
        print(f"Ответ RAG-консультанта:\n{reply}\n")
    except Exception as ask_err:
        print(f"Ошибка вызова ask_consultant: {ask_err}")

if __name__ == "__main__":
    main()
