import io
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

# ==============================================================================
# ШРИФТЫ И ПОДДЕРЖКА КИРИЛЛИЦЫ (UTF-8)
# ==============================================================================
FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"

def _register_cyrillic_fonts():
    """
    Регистрирует TrueType шрифты с поддержкой кириллицы (UTF-8).
    Автоматически ищет шрифты в стандартных путях Linux/Docker и Windows.
    """
    if FONT_REGULAR in pdfmetrics.getRegisteredFontNames():
        return

    candidate_pairs = [
        # 1. Linux / Docker (пакет fonts-dejavu-core)
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ),
        (
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
        ),
        # 2. Windows стандартные шрифты
        (
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
        ),
        (
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/calibrib.ttf"
        ),
        (
            "C:/Windows/Fonts/seguiemj.ttf",
            "C:/Windows/Fonts/seguisb.ttf"
        )
    ]

    for reg_path, bold_path in candidate_pairs:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont(FONT_REGULAR, reg_path))
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont(FONT_BOLD, bold_path))
                else:
                    pdfmetrics.registerFont(TTFont(FONT_BOLD, reg_path))
                logger.info(f"[PDF FONTS] Зарегистрированы шрифты из {reg_path}")
                return
            except Exception as e:
                logger.warning(f"[PDF FONTS] Ошибка регистрации шрифта {reg_path}: {e}")

    logger.warning("[PDF FONTS] Шрифты с поддержкой UTF-8 не найдены в стандартных путях, используется фоллбэк Helvetica.")


# ==============================================================================
# КАСТОМНЫЙ CANVAS ДЛЯ ПОДВАЛА И НУМЕРАЦИИ СТРАНИЦ
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    """
    Двухпроходный Canvas ReportLab для точного вычисления и печати
    номера страницы («Стр. X из Y») и дисклеймера на каждой странице.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        font_to_use = FONT_REGULAR if FONT_REGULAR in pdfmetrics.getRegisteredFontNames() else "Helvetica"
        
        # Линия разделителя подвала
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(40, 48, A4[0] - 40, 48)

        # Дисклеймер (слева)
        self.setFont(font_to_use, 7)
        self.setFillColor(colors.HexColor("#64748B"))
        disclaimer = "Справочный документ ИИ-системы. Окончательное клиническое решение принимает лечащий врач."
        self.drawString(40, 34, disclaimer)
        self.drawString(40, 24, "Центр медицинского здоровья и развития «Маленькая Страна» | цмз.site")

        # Номер страницы (справа)
        page_text = f"Стр. {self._pageNumber} из {total_pages}"
        self.setFont(font_to_use, 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawRightString(A4[0] - 40, 34, page_text)

        self.restoreState()


# ==============================================================================
# ГЕНЕРАТОР PDF-РЕЗЮМЕ
# ==============================================================================
def generate_summary_pdf(
    summary_data: Dict[str, Any],
    doctor_info: Dict[str, Any],
    patient_folder_id: str
) -> bytes:
    """
    Генерирует медицинское резюме пациента в формате PDF на основе данных RAG-анализа.
    
    Структура документа:
    - Шапка: Название клиники, Заголовок, Подзаголовок, Метаданные (Врач, Лицензия, Пациент, Дата)
    - 1. Анамнез и текущее состояние
    - 2. Клинические диагнозы
    - 3. Критические противопоказания и аллергии (выделены предупреждающим блоком)
    - 4. Несовместимые препараты и риски взаимодействий (выделены предупреждающим блоком)
    - 5. Рекомендации по наблюдению
    - Подвал: Дисклеймер и нумерация страниц (Стр. X из Y)

    :param summary_data: Словарь с полями anamnesis, diagnoses, contraindications, drug_interactions, recommendations
    :param doctor_info: Словарь с данными врача (full_name, specialty, license_number)
    :param patient_folder_id: Идентификатор папки пациента
    :return: Бинарные данные PDF-файла (bytes)
    """
    _register_cyrillic_fonts()

    font_reg = FONT_REGULAR if FONT_REGULAR in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    font_bold = FONT_BOLD if FONT_BOLD in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=60
    )

    # Цветовая палитра клиники
    COLOR_PRIMARY = colors.HexColor("#1E1E2E")      # Темный базовый
    COLOR_ACCENT = colors.HexColor("#7C3AED")       # Фиолетовый акцент
    COLOR_TEXT = colors.HexColor("#334155")         # Основной текст
    COLOR_MUTED = colors.HexColor("#64748B")        # Второстепенный текст
    COLOR_DANGER_BG = colors.HexColor("#FEF2F2")    # Фон для аллергий / противопоказаний
    COLOR_DANGER_BORDER = colors.HexColor("#EF4444")# Красная рамка
    COLOR_DANGER_TEXT = colors.HexColor("#991B1B")  # Темно-красный текст
    COLOR_CARD_BG = colors.HexColor("#F8FAFC")      # Светлый фон блоков

    # Стили текста
    styles = getSampleStyleSheet()

    clinic_name_style = ParagraphStyle(
        "ClinicName",
        fontName=font_bold,
        fontSize=9,
        leading=12,
        textColor=COLOR_ACCENT,
        alignment=TA_LEFT
    )

    doc_title_style = ParagraphStyle(
        "DocTitle",
        fontName=font_bold,
        fontSize=18,
        leading=22,
        textColor=COLOR_PRIMARY,
        alignment=TA_LEFT
    )

    doc_subtitle_style = ParagraphStyle(
        "DocSubtitle",
        fontName=font_reg,
        fontSize=10,
        leading=13,
        textColor=COLOR_MUTED,
        alignment=TA_LEFT
    )

    section_header_style = ParagraphStyle(
        "SectionHeader",
        fontName=font_bold,
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=10,
        spaceAfter=4
    )

    section_danger_header_style = ParagraphStyle(
        "SectionDangerHeader",
        fontName=font_bold,
        fontSize=11,
        leading=15,
        textColor=COLOR_DANGER_TEXT
    )

    body_text_style = ParagraphStyle(
        "BodyText",
        fontName=font_reg,
        fontSize=10,
        leading=14,
        textColor=COLOR_TEXT,
        alignment=TA_JUSTIFY
    )

    list_item_style = ParagraphStyle(
        "ListItem",
        fontName=font_reg,
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_TEXT,
        leftIndent=14
    )

    danger_item_style = ParagraphStyle(
        "DangerItem",
        fontName=font_reg,
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_DANGER_TEXT,
        leftIndent=14
    )

    meta_label_style = ParagraphStyle(
        "MetaLabel",
        fontName=font_bold,
        fontSize=8.5,
        leading=11,
        textColor=COLOR_MUTED
    )

    meta_val_style = ParagraphStyle(
        "MetaVal",
        fontName=font_reg,
        fontSize=9.5,
        leading=12,
        textColor=COLOR_PRIMARY
    )

    story = []

    # 1. ШАПКА ДОКУМЕНТА
    story.append(Paragraph("ЦЕНТР МЕДИЦИНСКОГО ЗДОРОВЬЯ И РАЗВИТИЯ «МАЛЕНЬКАЯ СТРАНА»", clinic_name_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("МЕДИЦИНСКОЕ РЕЗЮМЕ ПАЦИЕНТА", doc_title_style))
    story.append(Paragraph("Сгенерировано ИИ-Консультантом клиники (цмз.site)", doc_subtitle_style))
    story.append(Spacer(1, 8))

    # Линия акцента
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_ACCENT, spaceBefore=0, spaceAfter=8))

    # 2. МЕТАДАННЫЕ (Таблица)
    clean_patient_name = patient_folder_id.replace("disk:/", "").strip()
    doctor_name = doctor_info.get("full_name") or "Специалист Клиники"
    doctor_license = doctor_info.get("license_number") or doctor_info.get("specialty") or "Верифицированный врач"
    gen_date = datetime.now().strftime("%d.%m.%Y %H:%M")

    meta_data = [
        [
            Paragraph("ПАЦИЕНТ / КАРТА:", meta_label_style),
            Paragraph(clean_patient_name, meta_val_style),
            Paragraph("ДАТА ГЕНЕРАЦИИ:", meta_label_style),
            Paragraph(gen_date, meta_val_style)
        ],
        [
            Paragraph("ВРАЧ-СПЕЦИАЛИСТ:", meta_label_style),
            Paragraph(doctor_name, meta_val_style),
            Paragraph("ЛИЦЕНЗИЯ / ПРОФИЛЬ:", meta_label_style),
            Paragraph(doctor_license, meta_val_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 110, 135])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_CARD_BG),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Проверка на наличие ошибки в ответе LLM
    if "raw_response" in summary_data and not summary_data.get("anamnesis"):
        story.append(Paragraph("СЫРОЙ ОТЧЕТ АНАЛИЗА", section_header_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(str(summary_data["raw_response"]), body_text_style))
        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()

    # 3. СЕКЦИЯ: АНАМНЕЗ
    anamnesis_text = summary_data.get("anamnesis") or "Данные анамнеза в предоставленных документах отсутствуют."
    story.append(Paragraph("1. АНАМНЕЗ И ТЕКУЩЕЕ СОСТОЯНИЕ", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(anamnesis_text, body_text_style))
    story.append(Spacer(1, 12))

    # 4. СЕКЦИЯ: ДИАГНОЗЫ
    diagnoses = summary_data.get("diagnoses") or []
    story.append(Paragraph("2. УСТАНОВЛЕННЫЕ ДИАГНОЗЫ", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=6))
    if diagnoses and isinstance(diagnoses, list):
        for idx, d in enumerate(diagnoses, 1):
            story.append(Paragraph(f"• <b>{d}</b>", list_item_style))
            story.append(Spacer(1, 2))
    elif diagnoses and isinstance(diagnoses, str):
        story.append(Paragraph(diagnoses, body_text_style))
    else:
        story.append(Paragraph("Диагнозы в медицинских документах не зафиксированы.", body_text_style))
    story.append(Spacer(1, 12))

    # 5. СЕКЦИЯ: ПРОТИВОПОКАЗАНИЯ И АЛЛЕРГИИ (ALERT BOX)
    contraindications = summary_data.get("contraindications") or []
    contra_items = []
    if contraindications and isinstance(contraindications, list):
        for c in contraindications:
            contra_items.append(Paragraph(f"⚠️ {c}", danger_item_style))
    elif contraindications and isinstance(contraindications, str):
        contra_items.append(Paragraph(f"⚠️ {contraindications}", danger_item_style))
    else:
        contra_items.append(Paragraph("Критических противопоказаний и аллергических реакций не выявлено.", list_item_style))

    contra_content = [
        [Paragraph("⚠️ КРИТИЧЕСКИЕ ПРОТИВОПОКАЗАНИЯ И АЛЛЕРГИИ", section_danger_header_style)],
        [HRFlowable(width="100%", thickness=0.5, color=COLOR_DANGER_BORDER, spaceBefore=2, spaceAfter=4)]
    ]
    for item in contra_items:
        contra_content.append([item])

    contra_table = Table(contra_content, colWidths=[515])
    contra_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_DANGER_BG),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_DANGER_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(KeepTogether([contra_table]))
    story.append(Spacer(1, 12))

    # 6. СЕКЦИЯ: НЕСОВМЕСТИМЫЕ ПРЕПАРАТЫ (ALERT BOX)
    drug_interactions = summary_data.get("drug_interactions") or []
    drug_items = []
    if drug_interactions and isinstance(drug_interactions, list):
        for d in drug_interactions:
            drug_items.append(Paragraph(f"⛔ {d}", danger_item_style))
    elif drug_interactions and isinstance(drug_interactions, str):
        drug_items.append(Paragraph(f"⛔ {drug_interactions}", danger_item_style))
    else:
        drug_items.append(Paragraph("Сведений о несовместимости препаратов нет.", list_item_style))

    drug_content = [
        [Paragraph("⛔ НЕСОВМЕСТИМЫЕ ПРЕПАРАТЫ И ЛЕКАРСТВЕННЫЕ ВЗАИМОДЕЙСТВИЯ", section_danger_header_style)],
        [HRFlowable(width="100%", thickness=0.5, color=COLOR_DANGER_BORDER, spaceBefore=2, spaceAfter=4)]
    ]
    for item in drug_items:
        drug_content.append([item])

    drug_table = Table(drug_content, colWidths=[515])
    drug_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#F59E0B")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(KeepTogether([drug_table]))
    story.append(Spacer(1, 12))

    # 7. СЕКЦИЯ: РЕКОМЕНДАЦИИ
    recommendations = summary_data.get("recommendations") or []
    story.append(Paragraph("3. РЕКОМЕНДАЦИИ ПО НАБЛЮДЕНИЮ И ТЕРАПИИ", section_header_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=6))
    if recommendations and isinstance(recommendations, list):
        for idx, r in enumerate(recommendations, 1):
            story.append(Paragraph(f"{idx}. {r}", list_item_style))
            story.append(Spacer(1, 2))
    elif recommendations and isinstance(recommendations, str):
        story.append(Paragraph(recommendations, body_text_style))
    else:
        story.append(Paragraph("Специальные рекомендации отсутствуют.", body_text_style))

    # Сборка документа с двухпроходным нумератором страниц
    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()

