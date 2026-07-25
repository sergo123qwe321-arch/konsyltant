import sys
from drive_api import get_drive_service

def main():
    print("Проверка подключения к Google Drive API...")
    service = get_drive_service()
    if not service:
        print("Ошибка: Не удалось получить сервис Google Drive.")
        sys.exit(1)
        
    try:
        print("Запрашиваем список файлов...")
        results = service.files().list(
            pageSize=50, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])
        
        if not items:
            print("Папки/файлы не найдены. Возможно, папка еще не расшарена для сервисного аккаунта.")
        else:
            print(f"Успех! Найдено {len(items)} файлов/папок:")
            for item in items:
                print(f" - {item['name']} (ID: {item['id']}, Type: {item['mimeType']})")
    except Exception as e:
        print(f"Произошла ошибка при запросе к API: {e}")

if __name__ == '__main__':
    main()
