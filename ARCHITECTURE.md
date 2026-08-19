# ИИ-Консультант RAG API: Архитектура и Технический Канвас

## 🎯 Project Overview
«ИИ-Консультант RAG API» — высоконадежная платформа персонального медицинского ассистента на базе RAG (Retrieval-Augmented Generation) и открытого информационного портала клиники «Маленькая Страна».

---

## 🛠️ Tech Stack
- **Язык программирования:** Python 3.13
- **Веб-фреймворк:** FastAPI (Uvicorn, Starlette)
- **Шаблонизатор:** Jinja2
- **Веб-сервер / Reverse Proxy:** Nginx (Alpine) — кэширование статики 30d, проксирование бэкенда
- **Базы данных:** PostgreSQL 15 (Docker) / SQLite3 (локально)
- **Безопасность & Аутентификация:**
  - Stateless JWT (`PyJWT`, алгоритм `HS256`, время жизни токена 30 минут, `Bearer` авторизация)
  - Хэширование паролей (`bcrypt`)
  - Шифрование Data at Rest (`cryptography.fernet`)
- **API & Интеграции:**
  - GigaChat API (RAG-генерация ответов)
  - Yandex Disk API (облачное хранилище и кэш)
  - Google Drive API (резервный источник)
  - Yandex SMTP (уведомления)
- **Обработка данных & OCR:**
  - `pytesseract` + `tesseract-ocr-rus` (распознавание текста с изображений и сканов)
  - `PyMuPDF`, `pdf2image`, `poppler-utils`, `python-docx` (парсинг документов)

---

## 📁 Структура проекта

```text
antigravKONSYLTANT/
│
├── nginx/                      # Конфигурация Nginx Reverse Proxy
│   └── default.conf            # Роутинг /, /app/, прямое кэширование /static/
│
├── templates/                  # Jinja2 HTML шаблоны
│   └── index.html              # Главный лендинг (Hero, Персонажи Pixar, Услуги, Врачи, Блог)
│
├── static/                     # Статические ресурсы (прямая раздача Nginx)
│   ├── css/
│   │   └── style.css           # Стили темы клиники (#1E1E2E, #7C3AED, #06B6D4)
│   ├── js/
│   │   ├── bubbles.js          # Canvas интерактивная анимация пузырьков снов
│   │   └── app.js              # Клиентский UI, Showcase персонажей, модалки, REST API клиент
│   ├── images/                 # 3D Pixar персонажи звуков (char_a.jpg ... char_y.jpg)
│   ├── audio/                  # Звуковые сэмплы инструментов (sound_a.mp3 ... sound_y.mp3)
│   └── index.html              # SPA-интерфейс приватного чата пациента (/app/)
│
├── main.py                     # Точка входа FastAPI (REST API, JWT Auth Middleware, роутинг)
├── database.py                 # Схема PostgreSQL/SQLite, RBAC, Seeding тестовых данных
├── security_utils.py           # Stateless JWT (генерация, валидация, проверка TTL)
├── crypto_utils.py             # Data at Rest Encryption (Fernet) + реэкспорт security_utils
├── rag.py                      # RAG пайплайн (GigaChat API + изоляция контекста пациента)
├── folder_watcher.py           # Фоновый воркер синхронизации Яндекс.Диска
├── document_parser.py          # Гибридный парсер документов (DOCX, PDF, OCR Tesseract)
├── notification_service.py     # Yandex SMTP сервис рассылки доступов
│
├── Dockerfile                  # Контейнеризация Python 3.13 + Tesseract OCR + Poppler
├── docker-compose.yml          # Оркестрация: konsyltant_nginx, konsyltant_web, konsyltant_db
├── .dockerignore               # Исключение служебных файлов и scripts/ из сборки
├── requirements.txt            # Зависимости проекта
├── process.md                  # Единый журнал прогресса и истории проекта
├── ARCHITECTURE.md             # Архитектурный канвас и техническая спецификация
└── scripts/                    # Вспомогательные скрипты (вне Docker)
    ├── README.md               # Документация служебных утилит
    ├── admin/reset_db.py       # Локальная очистка тестовой БД
    └── debug/inspect_*.py      # Ручная диагностика Yandex Disk API
```

---

## 📋 БИЗНЕС-ПРОЦЕСС: ОБРАБОТКА МЕДИЦИНСКИХ ДОКУМЕНТОВ

1. **Загрузка документов:**
   - Администратор клиники загружает папку с медицинскими документами ребенка на Яндекс.Диск.

2. **ETL-обработка (`folder_watcher.py`):**
   - Фоновый воркер непрерывно мониторит появление новых папок на Яндекс.Диске.
   - При обнаружении новой папки вызывается гибридный парсер `document_parser.py`.
   - Парсер извлекает текст из документов (DOCX, PDF, сканы через OCR Tesseract) и разбивает его на чанки.
   - Создается файл `_{имя_пациента}_cache.json` В ТОЙ ЖЕ папке на Яндекс.Диске (префикс `_` защищает от зацикливания сканера).

3. **Генерация доступа:**
   - В базу данных PostgreSQL сохраняется запись:
     * `access_token` (секретный токен / ключ для пациента)
     * `password_hash` (хэш пароля по алгоритму bcrypt)
     * `gdrive_folder_id` (идентификатор папки пациента на Яндекс.Диске)
     * ссылка на веб-приложение ИИ-Консультанта (`/app/?token=...`)

4. **Изоляция данных (Multi-Tenant Isolation):**
   - ИИ-Консультант (RAG-пайплайн в `rag.py`) работает **ТОЛЬКО** с файлом чанков из конкретной папки пациента.
   - Stateless JWT токен сессии пациента содержит жестко зашитый клейм `allowed_folder`, исключая cross-tenant доступ.

5. **Передача доступов:**
   - Ссылка и пароль автоматически отправляются через защищенный SMTP на email: `konsultantms@yandex.com`.
   - Администратор **ЛИЧНО** передает сформированные доступы родителю ребенка.
   - Родитель авторизуется в системе и общается с персональным ИИ-Консультантом.

> 🔒 **АРХИТЕКТУРНЫЙ ПРИНЦИП:** Каждая папка пациента = строго изолированный контекст для RAG. Никакого cross-tenant доступа.

---

## 🇷🇺 АРХИТЕКТУРНЫЙ ИМПЕРАТИВ: ТЕХНОЛОГИЧЕСКИЙ СУВЕРЕНИТЕТ

> **ДИРЕКТИВА:** Система должна стабильно и автономно функционировать на территории РФ без использования VPN, обходных прокси и зависеть только от сервисов, устойчивых к блокировкам РКН и санкциям иностранных компаний. Все критичные интеграции должны иметь отечественные аналоги или локальные фоллбэки.

### Матрица аудита внешних интеграций:

| Сервис / Технология | Юрисдикция | Риск блокировки | Текущий фоллбэк | Статус и Рекомендация |
| :--- | :--- | :--- | :--- | :--- |
| **GigaChat API (Сбер)** | РФ | **Низкий** | — | ✅ **Соответствует.** Основной RAG LLM провайдер, отечественный хостинг, 152-ФЗ. |
| **Yandex Disk API** | РФ | **Низкий** | Локальное файловое кэширование | ✅ **Соответствует.** Основное облачное хранилище документов и чанков. |
| **Google Drive API** | США | **Высокий** | Graceful 503 / Понятное сообщение в UI | ⚠️ **Наследие MVP.** Рекомендуется полный перевод на отечественный S3 (VK Cloud / Selectel / MinIO). |
| **Yandex SMTP / UniSender** | РФ | **Низкий** | Логирование доступов в защищенный журнал | ✅ **Соответствует.** Отечественные почтовые шлюзы с TLS 465. |
| **Let's Encrypt / Certbot** | США | **Средний** | `nginx/init-ssl.sh` (Self-signed) | ✅ **Защищено.** Скрипт `init-ssl.sh` создает локальный сертификат при сбое ACME. Рекомендуется подключение сертификатов Минцифры РФ / Госуслуг. |

---

## 🏗️ System Architecture

1. **Edge / Reverse Proxy Layer (Nginx):**
   - Порт `80`, `443` -> Проксирование запросов к FastAPI (`http://web:8000`), SSL-терминация.
   - `/` -> Отдача SSR шаблона лендинга `templates/index.html`.
   - `/app/` -> Приватный SPA чат пациента.
   - `/static/` -> Прямая отдача CSS/JS/Images/Audio с заголовками кэширования на 30 дней.

2. **API & Security Layer (FastAPI):**
   - Stateless JWT-аутентификация: Защищенные эндпоинты `/api/chat` и `/api/patient/files` требуют заголовок `Authorization: Bearer <token>`.
   - Административная CMS-панель: Эндпоинты `/api/v1/admin/*` защищены JWT с верификацией роли `ADMIN`.
   - Кабинет врача (Doctor Portal): Эндпоинты `/api/v1/doctor/*` защищены JWT с верификацией роли `DOCTOR`.
   - Автоматический таймаут неактивности (30 минут).
   - Публичные REST API (`/api/v1/public/services`, `/doctors`, `/posts`, `/events`, `/leads`).
   - Домен: `цмз.site` (Punycode `xn--g1aj3a.site`, `www.xn--g1aj3a.site`), VPS IP `159.194.232.74`.

3. **Background ETL & Storage Layer:**
   - `folder_watcher.py` отслеживает появление медицинских карт на Яндекс.Диске.
   - `document_parser.py` извлекает текст (с поддержкой OCR и постраничной защитой от сбоев).
   - `rag.py` изолирует медицинский контекст строго в рамках разрешенной папки пациента (`allowed_folder`).

4. **Database Indexing & Query Optimization:**
   - **Автомиграция индексов (`ensure_indexes`):** При каждом старте `init_db()` проверяет и идемпотентно создает B-tree индексы в PostgreSQL и SQLite.
   - **Уникальные индексы токенов:** `idx_patient_access_token` на `patient_access(access_token)` и `idx_share_grants_token` на `patient_share_grants(share_token)` обеспечивают $O(\log N)$ валидацию токенов.
   - **Составные индексы (Composite Indexes):**
     - `idx_share_grants_patient_active` на `(patient_folder_id, is_active, expires_at)` для моментального подсчета активных ссылок.
     - `idx_patient_access_role_verified` на `(role, is_verified)` для выборки врачей.
     - `idx_public_leads_status_created` на `(status, created_at)` для фильтрации заявок в CMS.
   - **Индексы сортировки и внешних ключей:** `idx_public_posts_created_at`, `idx_share_grants_doctor_id`, `idx_doctors_license_number`.

---

## 🛡️ Fault Tolerance, Security & Rate Limiting Policy
- **Rate Limiting (Защита от Brute-Force):**
  - Ограничение частоты запросов на endpoints авторизации (`/api/login`, `/api/v1/doctor/login`, `/api/v1/admin/login`).
  - Лимит: максимум 5 попыток в минуту с одного IP-адреса (с поддержкой `X-Forwarded-For`).
  - Период блокировки: 5 минут (300 секунд) с возвратом HTTP 429, заголовком `Retry-After: 300` и безопасным маскированием IP в логах (`mask_ip`).
  - Авто-сброс: при успешной авторизации (HTTP 200) счетчик неудачных попыток для IP сбрасывается.
  - Fail-Open стратегия: при непредвиденных сбоях ограничителя запросы пропускаются без блокировки пользователей.
- Ограничение времени (`timeout=60s`) на OCR-парсинг с постраничной изоляцией.
- Жесткие сетевые таймауты (`timeout=15s`) для внешних HTTP-запросов.
- Graceful Degradation: при сбоях GigaChat API возвращается понятная ошибка без падения сервиса.
- Mock-данные на фронтенде: лендинг сохраняет работоспособность даже при временной недоступности бэкенда.

---

## 🚀 Roadmap & Status

### ✅ Phase 1: Infrastructure & Security Core (Завершена)
- [x] **Nginx Reverse Proxy:** Маршрутизация на 80 порту, изоляция сервиса web во внутренней сети Docker, привязка домена `цмз.site`.
- [x] **Data at Rest Encryption:** Модуль `crypto_utils.py` (Fernet) для шифрования медицинских данных.
- [x] **RBAC Foundation:** Таблицы ролей (`PATIENT`, `DOCTOR`, `ADMIN`) и таблица заявок `public_leads`.
- [x] **Stateless JWT Migration:** Полный отказ от серверной памяти сессий, время жизни токена 30 минут.

### ✅ Phase 2: Public Portal, Expert Blog & Admin CMS (Завершена)
- [x] **Модуляризация фронтенда:** Выделение `templates/index.html`, `style.css`, `bubbles.js`, `app.js`.
- [x] **Анимация снов (Bubbles):** Полноэкранный отзывчивый Canvas с градиентами и эффектом отталкивания курсора.
- [x] **Экспертный блог:** 3 практические статьи от нейропсихологов и логопедов, модальный просмотр статей.
- [x] **Сбор заявок (Leads):** Интерактивная форма записи родителей с валидацией и сохранением в БД.
- [x] **Административная CMS:** Веб-панель управления заявками клиентов и публикациями статей блога (CRUD).
- [x] **Интерактивный блок персонажей Pixar:** 6 героев звуков, анимация Pixar Bounce, звуковые эффекты инструментов.
- [x] **Отказоустойчивость UI:** Офлайн-моки и резервные эмодзи при отсутствии соединения.

### ✅ Phase 3: Doctor's Dashboard & Data Sharing (Завершена)
- [x] **Схема и API шеринга:** Таблицы `doctors`, `patient_share_grants`, эндпоинты `/api/v1/doctor/login`, `/api/v1/patient/share`, `/api/v1/doctor/patient-records/{share_token}`.
- [x] **UI кабинета врача & глубокие ссылки:** Полнофункциональный Doctor Dashboard (`#doctor-dashboard-modal`) с поддержкой deep-linking `?share_token=...`.
- [x] **UI шеринга в SPA пациента:** Модальное окно генерации временной ссылки (`#share-modal`) с выбором TTL и копированием в буфер.
- [x] **Rate Limiting & DB Indexes:** Защита авторизации от brute-force и B-tree индексы БД с автомиграцией.

### ⏳ Phase 4: AI Enhancements (Client App)
- [ ] **Voice-to-Text:** Интеграция Native Web Speech API на фронтенде чата.
- [ ] **Medical Analytics:** Пайплайн суммаризации и модуль проверки противопоказаний на базе LLM.



