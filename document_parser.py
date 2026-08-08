import io
import logging
from PIL import Image
import PyPDF2
import docx

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pdf2image
except ImportError:
    pdf2image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

logger = logging.getLogger(__name__)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """
    Разбивает текст на смысловые фрагменты (чанки) с учетом границ строк и пробелов.
    """
    if not text or not text.strip():
        return []
    cleaned_text = text.strip()
    if len(cleaned_text) <= chunk_size:
        return [cleaned_text]

    chunks = []
    start = 0
    while start < len(cleaned_text):
        end = start + chunk_size
        if end < len(cleaned_text):
            # Разрыв по символу переноса строки или пробелу
            last_newline = cleaned_text.rfind('\n', start, end)
            if last_newline > start + chunk_size // 2:
                end = last_newline + 1
            else:
                last_space = cleaned_text.rfind(' ', start, end)
                if last_space > start + chunk_size // 2:
                    end = last_space + 1

        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end < len(cleaned_text) else len(cleaned_text)

    return chunks

def parse_document_bytes(file_bytes: bytes, file_name: str, mime_type: str = "") -> str:
    """
    Гибридный парсер медицинских документов с поддержкой Tesseract OCR.
    Поддерживаемые форматы: .pdf (текст + сканы), .docx, .png, .jpg, .jpeg, .txt.
    """
    fname_lower = file_name.lower()
    
    # 1. Текстовые файлы (.txt)
    if fname_lower.endswith('.txt') or mime_type == 'text/plain':
        try:
            text = file_bytes.decode('utf-8', errors='ignore')
            print(f"[SECURE PARSER LOG] Извлечено {len(text)} символов через Text Decoder из '{file_name}'")
            return text
        except Exception as e:
            return f"[Ошибка чтения txt файла {file_name}: {e}]"

    # 2. Файлы Word (.docx)
    elif fname_lower.endswith('.docx') or 'word' in mime_type:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            print(f"[SECURE PARSER LOG] Извлечено {len(text)} символов через DOCX Parser из '{file_name}'")
            return text
        except Exception as e:
            return f"[Ошибка чтения docx файла {file_name}: {e}]"

    # 3. Картинки (.png, .jpg, .jpeg) — прямой OCR
    elif fname_lower.endswith(('.png', '.jpg', '.jpeg')) or 'image' in mime_type:
        if not pytesseract:
            print(f"[PARSER WARNING] pytesseract не установлен. Невозможно выполнить OCR для '{file_name}'")
            return f"[Отказ OCR: pytesseract не доступен в среде]"
        try:
            image = Image.open(io.BytesIO(file_bytes))
            ocr_text = pytesseract.image_to_string(image, lang='rus', timeout=60)
            print(f"[SECURE PARSER LOG] Извлечено {len(ocr_text)} символов через Image OCR (pytesseract lang=rus) из '{file_name}'")
            return ocr_text
        except Exception as e:
            print(f"[PARSER ERROR] Сбой/таймаут Image OCR для {file_name}: {e}")
            return f"[Ошибка OCR изображения {file_name}: {e}]"

    # 4. Гибридный парсинг PDF (Текстовый слой -> OCR скан)
    elif fname_lower.endswith('.pdf') or mime_type == 'application/pdf':
        text_layer = ""
        
        # Шаг 4.1. Извлечение текстового слоя через PyMuPDF (fitz) или PyPDF2
        if fitz:
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                pages_text = [page.get_text() for page in doc]
                text_layer = "\n".join([p for p in pages_text if p.strip()])
            except Exception as e:
                logger.warning(f"PyMuPDF failed on {file_name}: {e}")

        if not text_layer.strip():
            try:
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                pages_text = [page.extract_text() for page in reader.pages]
                text_layer = "\n".join([p for p in pages_text if p and p.strip()])
            except Exception as e:
                logger.warning(f"PyPDF2 failed on {file_name}: {e}")

        # Если текстовый слой найден (не скан)
        if len(text_layer.strip()) > 30:
            print(f"[SECURE PARSER LOG] Извлечено {len(text_layer)} символов через PDF Text Extraction (PyMuPDF/PyPDF2) из '{file_name}'")
            return text_layer

        # Шаг 4.2. Текстовый слой пуст -> Сканированный PDF -> OCR через pdf2image + pytesseract
        print(f"[PARSER LOG] PDF '{file_name}' не содержит текстового слоя. Запуск сканирующего гибрида (pdf2image + pytesseract)...")
        if pdf2image and pytesseract:
            try:
                images = pdf2image.convert_from_bytes(file_bytes)
                ocr_pages = []
                for idx, img in enumerate(images):
                    try:
                        page_text = pytesseract.image_to_string(img, lang='rus', timeout=60)
                        if page_text.strip():
                            ocr_pages.append(page_text)
                    except Exception as page_err:
                        print(f"[PARSER WARNING] Страница {idx+1} в '{file_name}' была пропущена из-за ошибки/таймаута OCR: {page_err}")

                ocr_full = "\n".join(ocr_pages)
                print(f"[SECURE PARSER LOG] Извлечено {len(ocr_full)} символов через PDF OCR Engine (pdf2image + pytesseract lang=rus, страниц: {len(images)}) из '{file_name}'")
                return ocr_full
            except Exception as e:
                print(f"[PARSER ERROR] Сбой PDF OCR для {file_name}: {e}")
                return f"[Ошибка PDF OCR для {file_name}: {e}]"
        else:
            print(f"[PARSER WARNING] Системные пакеты pdf2image/pytesseract недоступны. Скан '{file_name}' не прочитан.")
            return f"[Скан PDF не прочитан: требуются pdf2image и pytesseract в Docker-образе]"

    else:
        return f"[Неподдерживаемый формат файла: {file_name}]"
