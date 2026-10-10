"""
test_bootstrap.py — единая точка входа тестового окружения (Этап 7, шаг 7.2а).

Гарантирует, что весь прогон `python -m unittest discover -s . -p "test_*.py"`
выполняется строго в изолированной тестовой базе test_konsyltant.db.
Боевой файл konsyltant.db при этом не открывается и не изменяется.

Правило подключения: строка `import test_bootstrap` должна стоять САМОЙ ПЕРВОЙ
в каждом test_*.py модуле — до любых импортов `database` / `main`.
"""
import os

TEST_DB_FILE = "test_konsyltant.db"

# Окружение выставляется ДО импорта database/main: database.get_connection()
# перечитывает эти переменные на каждом соединении, load_dotenv() не перетирает
# уже установленные значения os.environ.
os.environ["SQLITE_DB_PATH"] = TEST_DB_FILE
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"

# Свежая тестовая база на каждый прогон: детерминированное состояние сидов,
# отсутствие накопленного мусора предыдущих прогонов.
try:
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
except OSError as exc:
    print(f"[TEST BOOTSTRAP] Не удалось удалить устаревший {TEST_DB_FILE}: {exc}")

import database  # noqa: E402  — импорт строго после настройки окружения

if database.DB_FILE != TEST_DB_FILE:
    raise RuntimeError(
        f"[TEST BOOTSTRAP] Изоляция нарушена: DB_FILE={database.DB_FILE!r}, "
        f"ожидалось {TEST_DB_FILE!r}"
    )

database.init_db()

# Базовые профили врачей в таблице `doctors`, чтобы проверки вида
# `len(doctors) >= 3` проходили гарантированно на чистой тестовой базе.
BASE_DOCTORS = (
    ("Доктор Продюсер", "Главный Продюсер / Клинический Эксперт", "PRODUCER-001", "producer@cmz.site"),
    ("Анна Сергеевна Волкова", "Ведущий нейропсихолог", "DOC-ANNA-001", "anna.volkova@cmz.site"),
    ("Михаил Андреевич Морозов", "Клинический логопед-дефектолог", "DOC-MIKHAIL-001", "mikhail.morozov@cmz.site"),
)

for _full_name, _specialty, _license, _email in BASE_DOCTORS:
    database.create_doctor(
        full_name=_full_name,
        specialty=_specialty,
        license_number=_license,
        is_verified=True,
        email=_email,
    )

# Материалы библиотеки: автономные SSR-страницы /library/{id} и тесты
# маршрутизации требуют existence хотя бы одной записи в public_library.
if not database.get_public_library_items():
    database.create_public_library_item(
        title="Как понять речевое развитие ребенка",
        summary="Ориентиры речевого развития от рождения до школы и сигналы, "
                "которые стоит обсудить со специалистом.",
        content="Речевое развитие ребенка — это последовательный процесс, "
                "который тесно связан с общим развитием, эмоциональным контактом "
                "и игровой активностью. Материал носит информационно-просветительский "
                "характер и не является медицинской рекомендацией.\n\n"
                "Первые годы особенно важны: ребенок учится слышать звук, повторять "
                "за взрослым и постепенно складывать слова в предложения. Если что-то "
                "в развитии вызывает вопросы, полезно обсудить их с профильным "
                "специалистом.",
        category="Развитие речи",
        tags=["речь", "развитие", "консультация"],
    )

print(f"[TEST BOOTSTRAP] Работаем в изолированной тестовой базе: {TEST_DB_FILE}")
