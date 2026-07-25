import io
import PyPDF2
import docx

def extract_text(file_bytes: bytes, mime_type: str, file_name: str) -> str:
    """
    Извлекает текст из файлов (.txt, .pdf, .docx).
    Также поддерживает нативные Google Docs, которые экспортируются как текст.
    """
    try:
        # Если это текстовый файл, ИЛИ это нативный Google Doc (который мы экспортируем в текст через drive_api.py)
        if mime_type == 'text/plain' or file_name.endswith('.txt') or mime_type == 'application/vnd.google-apps.document':
            return file_bytes.decode('utf-8')
            
        elif mime_type == 'application/pdf' or file_name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
            
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_name.endswith('.docx'):
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
            
        else:
            return f"[Неподдерживаемый формат файла: {file_name}]"
    except Exception as e:
        return f"[Ошибка парсинга {file_name}: {str(e)}]"
