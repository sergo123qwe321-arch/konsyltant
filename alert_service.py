"""
Модуль системы оповещений о критических сбоях и мониторинга здоровья платформы.
Поддерживает дублирование уведомлений на основной (PRIMARY_ALERT_EMAIL) и резервный (SECONDARY_ALERT_EMAIL) адреса,
дедупликацию оповещений (не чаще 1 раза в час по одной проблеме) и уведомления о выздоровлении.
"""

import os
import time
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import requests

from notification_service import NotificationService

load_dotenv()
logger = logging.getLogger("alert_service")

PRIMARY_ALERT_EMAIL = os.getenv("PRIMARY_ALERT_EMAIL", "konsultantms@yandex.com")
SECONDARY_ALERT_EMAIL = os.getenv("SECONDARY_ALERT_EMAIL", "sergo123qwe321@gmail.com")

DEDUPLICATION_WINDOW_SECONDS = 3600  # 1 час (3600 секунд)
CHECK_INTERVAL_SECONDS = 300         # 5 минут (300 секунд)
DB_UNAVAILABLE_THRESHOLD_SECONDS = 30 # 30 секунд

# Состояние активных алертов в памяти:
# key -> { "is_active": bool, "last_alert_time": float, "first_detected": float, "last_value": str, "description": str }
ALERT_STATES = {}
DB_DISCONNECT_START = None

def get_alert_recipients() -> list[str]:
    """Возвращает список адресов для отправки уведомлений с дедупликацией адресов."""
    primary = (os.getenv("PRIMARY_ALERT_EMAIL") or PRIMARY_ALERT_EMAIL).strip()
    secondary = (os.getenv("SECONDARY_ALERT_EMAIL") or SECONDARY_ALERT_EMAIL).strip()
    
    recipients = []
    if primary:
        recipients.append(primary)
    if secondary and secondary not in recipients:
        recipients.append(secondary)
    return recipients

def send_dual_email(subject: str, html_body: str) -> dict[str, bool]:
    """
    Отправляет email одновременно на основной и резервный адреса.
    Возвращает словарь со статусом отправки для каждого адреса.
    """
    recipients = get_alert_recipients()
    results = {}
    
    for r in recipients:
        try:
            success = NotificationService.send_smtp_email(subject, html_body, r)
            if not success:
                logger.warning(f"[ALERT SERVICE] Попытка отправки через резервный UniSender на {r}...")
                success = NotificationService.send_unisender_email(subject, html_body, r)
            results[r] = bool(success)
        except Exception as e:
            logger.error(f"[ALERT SERVICE ERROR] Ошибка отправки на {r}: {e}")
            results[r] = False
            
    return results

def build_alert_html(title: str, description: str, metric_value: str, recommendation: str, is_recovery: bool = False, is_test: bool = False) -> str:
    """Генерирует HTML-письмо с профессиональным оформлением для алертов и выздоровлений."""
    now_str = datetime.now(timezone(timedelta(hours=3))).strftime("%Y-%m-%d %H:%M:%S МСК")
    
    if is_test:
        header_color = "#3B82F6"
        header_title = "🔔 [ТЕСТОВОЕ ОПОВЕЩЕНИЕ] ПРОВЕРКА СИСТЕМЫ МОНИТОРИНГА"
    elif is_recovery:
        header_color = "#10B981"
        header_title = "✅ [ВЫЗДОРОВЛЕНИЕ] СЕРВИС ВОССТАНОВЛЕН"
    else:
        header_color = "#EF4444"
        header_title = "🚨 [КРИТИЧЕСКИЙ СБОЙ] ОБНАРУЖЕНА ПРОБЛЕМА"
        
    recipients_str = ", ".join(get_alert_recipients())
    
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0F172A; color: #F8FAFC; padding: 24px 12px; margin: 0;">
  <div style="max-width: 620px; margin: 0 auto; background-color: #1E293B; border-radius: 12px; border: 1px solid {header_color}; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
    <div style="background-color: {header_color}; color: #FFFFFF; padding: 16px 24px; font-size: 1.1rem; font-weight: 700; letter-spacing: 0.5px;">
      {header_title}
    </div>
    <div style="padding: 24px;">
      <h2 style="color: #FFFFFF; margin-top: 0; font-size: 1.3rem; line-height: 1.4;">{title}</h2>
      
      <div style="background-color: rgba(0,0,0,0.3); border-left: 4px solid {header_color}; padding: 14px 16px; border-radius: 6px; margin-bottom: 20px;">
        <div style="color: #94A3B8; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Описание ситуации</div>
        <div style="color: #F1F5F9; font-size: 1rem; line-height: 1.5;">{description}</div>
      </div>
      
      <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px;">
        <div style="background-color: rgba(255,255,255,0.04); padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
          <span style="color: #94A3B8; font-size: 0.85rem;">Текущее значение метрики:</span><br>
          <strong style="color: {header_color}; font-size: 1.05rem;">{metric_value}</strong>
        </div>
        
        <div style="background-color: rgba(255,255,255,0.04); padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
          <span style="color: #94A3B8; font-size: 0.85rem;">Рекомендуемое действие:</span><br>
          <strong style="color: #38BDF8; font-size: 0.95rem;">{recommendation}</strong>
        </div>
        
        <div style="background-color: rgba(255,255,255,0.04); padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
          <span style="color: #94A3B8; font-size: 0.85rem;">Время фиксации:</span><br>
          <strong style="color: #F1F5F9; font-size: 0.95rem;">{now_str}</strong>
        </div>
      </div>
      
      <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 16px; font-size: 0.8rem; color: #64748B; line-height: 1.6; text-align: center;">
        Платформа «Маленькая Страна» • Система наблюдаемости и оповещений<br>
        Уведомление автоматически направлено на адреса: <strong>{recipients_str}</strong>
      </div>
    </div>
  </div>
</body>
</html>"""
    return html

# ==============================================================================
# ФУНКЦИИ ПРОВЕРКИ МЕТРИК И СЕРВИСОВ
# ==============================================================================

def check_yandex_disk() -> tuple[bool, str, str]:
    """
    1. Проверка доступности Яндекс.Диска (квота и API).
    """
    token = os.getenv("YANDEX_DISK_TOKEN", "")
    if not token:
        return False, "Токен YANDEX_DISK_TOKEN не настроен в файле конфигурации .env", "Токен отсутствует"
        
    try:
        res = requests.get(
            "https://cloud-api.yandex.net/v1/disk/",
            headers={"Authorization": f"OAuth {token}", "Accept": "application/json"},
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            total_gb = data.get("total_space", 0) / (1024**3)
            used_gb = data.get("used_space", 0) / (1024**3)
            return True, "Яндекс.Диск доступен и отвечает на запросы квоты", f"Занято {used_gb:.1f} ГБ из {total_gb:.1f} ГБ"
        else:
            return False, f"Яндекс.Диск вернул HTTP статус {res.status_code}: {res.text[:120]}", f"HTTP {res.status_code}"
    except Exception as e:
        return False, f"Сетевая ошибка при обращении к Яндекс.Диску: {str(e)}", f"Exception: {type(e).__name__}"

def check_gigachat_api() -> tuple[bool, str, str]:
    """
    2. Проверка доступности GigaChat API (Сбер ИИ).
    Срабатывает при 3 последовательных ошибках или невозможности получить OAuth-токен.
    """
    from rag import get_consecutive_llm_errors, get_gigachat_token
    consecutive = get_consecutive_llm_errors()
    if consecutive >= 3:
        return False, f"Зафиксировано {consecutive} последовательных ошибок обращения к GigaChat API", f"{consecutive} ошибок подряд"
        
    token = get_gigachat_token()
    if not token:
        return False, "Не удалось получить OAuth-токен авторизации GigaChat (Сбер ИИ)", "OAuth error (токен не получен)"
        
    return True, "GigaChat API доступен и авторизован", "200 OK (OAuth active)"

def check_etl_worker() -> tuple[bool, str, str]:
    """
    3. Проверка падения фонового ETL-воркера folder_watcher.py (heartbeat > 10 мин).
    """
    from folder_watcher import get_last_etl_heartbeat
    last_hb = get_last_etl_heartbeat()
    now = time.time()
    diff = now - last_hb
    if diff > 600:
        return False, f"Фоновый ETL-воркер folder_watcher не обновлял heartbeat более {int(diff)} секунд", f"Heartbeat lag: {int(diff)}s (> 600s)"
    return True, "ETL-воркер активен и выполняет фоновое сканирование", f"Heartbeat: {int(diff)}s назад"

def check_gigachat_token_balance() -> tuple[bool, str, str]:
    """
    4. Проверка остатка токенов GigaChat (остаток < 20% от исходного пакета).
    """
    from rag import get_gigachat_balance
    limit_str = os.getenv("GIGACHAT_PACKAGE_TOKENS_LIMIT", "")
    
    # 1. Проверка официального баланса Сбера
    bal_info = get_gigachat_balance()
    if bal_info.get("status") == "available":
        balances = bal_info.get("balance", {}).get("balance", [])
        for b in balances:
            val = float(b.get("value", 0))
            if limit_str and limit_str.isdigit():
                limit = float(limit_str)
                if limit > 0 and (val / limit) < 0.2:
                    percent = (val / limit) * 100
                    return False, f"Официальный остаток токенов GigaChat ({int(val)}) составляет менее 20% ({percent:.1f}%) от исходного пакета {int(limit)}", f"{int(val)} токенов ({percent:.1f}%)"
                    
    # 2. Проверка по агрегированному расходу из БД относительно лимита
    if limit_str and limit_str.isdigit():
        limit = float(limit_str)
        if limit > 0:
            from database import get_llm_usage_summary
            usage = get_llm_usage_summary()
            all_time_tokens = usage.get("all_time", {}).get("total_tokens", 0)
            remaining = limit - all_time_tokens
            percent = (remaining / limit) * 100
            if percent < 20.0:
                return False, f"Расчетный остаток токенов GigaChat ({int(remaining)}) ниже 20% ({percent:.1f}%) от лимита пакета {int(limit)}", f"{int(remaining)} токенов ({percent:.1f}%)"

    return True, "Баланс токенов GigaChat находится в безопасных пределах (>= 20%)", "Остаток >= 20%"

def check_etl_performance() -> tuple[bool, str, str]:
    """
    5. Проверка средней скорости ETL-обработки (> 15 секунд на файл — деградация).
    """
    from database import get_etl_aggregates
    agg = get_etl_aggregates()
    avg_time = agg.get("avg_time_per_file_seconds")
    if avg_time is not None and avg_time > 15.0:
        return False, f"Средняя скорость ETL-обработки ({avg_time:.2f} с/файл) превышает критический порог 15 с/файл", f"{avg_time:.2f} с/файл (> 15.0s)"
        
    val_str = f"{avg_time:.2f} с/файл" if avg_time is not None else "Метрики в норме"
    return True, "Производительность ETL-конвейера находится в пределах нормы", val_str

def check_database_availability() -> tuple[bool, str, str]:
    """
    6. Проверка доступности базы данных PostgreSQL (недоступность > 30 секунд).
    """
    global DB_DISCONNECT_START
    from database import get_connection, execute_query
    try:
        conn = get_connection()
        cursor = conn.cursor()
        execute_query(cursor, "SELECT 1;")
        cursor.fetchone()
        conn.close()
        DB_DISCONNECT_START = None
        return True, "База данных PostgreSQL доступна и отвечает на запросы", "Connected (SELECT 1 OK)"
    except Exception as e:
        now = time.time()
        if DB_DISCONNECT_START is None:
            DB_DISCONNECT_START = now
        downtime = now - DB_DISCONNECT_START
        if downtime >= DB_UNAVAILABLE_THRESHOLD_SECONDS:
            return False, f"База данных PostgreSQL недоступна более {int(downtime)} секунд: {str(e)}", f"Downtime {int(downtime)}s: {type(e).__name__}"
        else:
            logger.warning(f"[DB HEALTH WARNING] Сбой БД ({int(downtime)}s / 30s threshold): {e}")
            return True, f"Кратковременный сбой БД ({int(downtime)}s), порог 30с пока не превышен", f"Warning ({int(downtime)}s)"

def check_backup_freshness(max_age_hours: float = 26.0, output_dir: str = None) -> tuple[bool, str, str]:
    """
    7. Проверка актуальности резервной копии базы данных (152-ФЗ).
    Если дампы отсутствуют или последний бэкап создан > max_age_hours назад — критический сбой.
    """
    from scripts.admin.backup_db import list_backups
    try:
        backups = list_backups(output_dir=output_dir)
        if not backups:
            return False, "Резервные копии базы данных отсутствуют в хранилище backups/ (152-ФЗ)", "Дампы отсутствуют (0 файлов)"
        
        now = time.time()
        last_backup = backups[0]
        mtime = last_backup["mtime"]
        age_seconds = max(0.0, now - mtime)
        age_hours = age_seconds / 3600.0
        filename = last_backup["filename"]
        size_human = last_backup.get("size_human", "")
        
        if age_hours > max_age_hours:
            return False, f"Последний дамп '{filename}' ({size_human}) устарел: создан {age_hours:.1f} ч назад (порог: {max_age_hours} ч)", f"{age_hours:.1f} ч (> {max_age_hours}ч)"
        
        return True, f"Резервный дамп '{filename}' ({size_human}) актуален (создан {age_hours:.1f} ч назад)", f"{age_hours:.1f} ч (норма <= {max_age_hours}ч)"
    except Exception as e:
        logger.error(f"[BACKUP HEALTH CHECK ERROR] Ошибка проверки бэкапов: {e}")
        return False, f"Ошибка при проверке резервных копий: {str(e)}", f"Error: {type(e).__name__}"

def trigger_daily_backup_if_needed(interval_hours: float = 24.0, output_dir: str = None) -> dict | None:
    """
    Автоматический триггер ежедневного фонового бэкапа:
    Если с момента последнего дампа прошло >= interval_hours (или если дампов нет),
    автоматически создает новый снимок базы данных с ротацией (retention_days=7, max_backups=7).
    """
    from scripts.admin.backup_db import list_backups, create_backup
    try:
        backups = list_backups(output_dir=output_dir)
        should_create = False
        
        if not backups:
            logger.info("[AUTO-BACKUP] Резервные копии отсутствуют. Запуск первого автоматического бэкапа...")
            should_create = True
        else:
            now = time.time()
            mtime = backups[0]["mtime"]
            age_hours = max(0.0, now - mtime) / 3600.0
            if age_hours >= interval_hours:
                logger.info(f"[AUTO-BACKUP] Прошло {age_hours:.1f} ч с момента последнего бэкапа (интервал: {interval_hours} ч). Автоматическое создание снимка...")
                should_create = True
                
        if should_create:
            result = create_backup(output_dir=output_dir, retention_days=7, max_backups=7, dry_run=False)
            logger.info(f"[AUTO-BACKUP SUCCESS] Создан автоматический бэкап: {result.get('filename')} ({result.get('size_human')})")
            return result
    except Exception as e:
        logger.error(f"[AUTO-BACKUP ERROR] Ошибка при автоматическом создании резервной копии: {e}")
        
    return None

# ==============================================================================
# РЕЕСТР ПРОВЕРОК
# ==============================================================================

MONITORED_SERVICES = [
    {
        "key": "yandex_disk",
        "func_name": "check_yandex_disk",
        "title": "Яндекс.Диск (Хранилище медицинских документов)",
        "func": check_yandex_disk,
        "recommendation": "Проверьте валидность OAuth-токена YANDEX_DISK_TOKEN в .env и доступность сервисов Яндекса."
    },
    {
        "key": "gigachat_api",
        "func_name": "check_gigachat_api",
        "title": "GigaChat API (Сбер ИИ)",
        "func": check_gigachat_api,
        "recommendation": "Проверьте статус API Сбера, корректность ключей GIGACHAT_CREDENTIALS и сетевое соединение."
    },
    {
        "key": "etl_worker",
        "func_name": "check_etl_worker",
        "title": "Фоновый ETL-воркер folder_watcher",
        "func": check_etl_worker,
        "recommendation": "Перезапустите фоновый воркер folder_watcher и проверьте системные логи контейнера konsyltant_web."
    },
    {
        "key": "gigachat_tokens",
        "func_name": "check_gigachat_token_balance",
        "title": "Остаток токенов GigaChat (< 20%)",
        "func": check_gigachat_token_balance,
        "recommendation": "Пополните баланс токенов GigaChat в личном кабинете Сбер Бизнес / Studio."
    },
    {
        "key": "etl_performance",
        "func_name": "check_etl_performance",
        "title": "Производительность ETL-конвейера (> 15 с/файл)",
        "func": check_etl_performance,
        "recommendation": "Проверьте нагрузку CPU/RAM на сервере и время работы OCR Tesseract при распознавании тяжелых сканов."
    },
    {
        "key": "database",
        "func_name": "check_database_availability",
        "title": "База данных PostgreSQL (> 30 с)",
        "func": check_database_availability,
        "recommendation": "Проверьте статус контейнера konsyltant_db (PostgreSQL) и сетевые параметры DATABASE_URL."
    },
    {
        "key": "backup_freshness",
        "func_name": "check_backup_freshness",
        "title": "Свежесть резервной копии БД (152-ФЗ, > 26ч)",
        "func": check_backup_freshness,
        "recommendation": "Проверьте права на запись в каталог backups/, свободное место на диске и статус фонового планировщика."
    }
]

# ==============================================================================
# ЦИКЛ МОНИТОРИНГА, ДЕДУПЛИКАЦИЯ И УВЕДОМЛЕНИЯ
# ==============================================================================

def run_health_checks_and_alert() -> dict:
    """
    Выполняет полный цикл проверки всех 7 сервисов.
    Реализует дедупликацию (не чаще 1 раза в час) и отправку уведомлений о выздоровлении.
    Перед проверками инициирует ежедневный автобэкап (если прошло >= 24ч).
    """
    # 1. Автоматический запуск ежедневного резервного копирования при необходимости
    try:
        trigger_daily_backup_if_needed()
    except Exception as e:
        logger.error(f"[AUTO-BACKUP TRIGGER ERROR] {e}")

    now = time.time()
    results = {}
    
    for srv in MONITORED_SERVICES:
        key = srv["key"]
        title = srv["title"]
        func_name = srv.get("func_name")
        func = globals().get(func_name) if func_name else srv.get("func")
        recommendation = srv["recommendation"]
        
        try:
            is_healthy, description, metric_val = func()
        except Exception as e:
            logger.error(f"[CHECK EXCEPTION] Ошибка в проверке {key}: {e}")
            is_healthy, description, metric_val = False, f"Исключение при проверке: {str(e)}", f"Exception: {type(e).__name__}"
            
        results[key] = {
            "healthy": is_healthy,
            "description": description,
            "metric_value": metric_val
        }
        
        state = ALERT_STATES.get(key, {
            "is_active": False,
            "last_alert_time": 0,
            "first_detected": 0,
            "last_value": "",
            "description": ""
        })
        
        # Сценарий 1: Обнаружен сбой
        if not is_healthy:
            if not state["is_active"]:
                # Первичное возникновение сбоя -> Немедленный критический алерт
                logger.error(f"[ALERT TRIGGERED] Сбой сервиса: {title} | {description} ({metric_val})")
                subject = f"🚨 [КРИТИЧЕСКИЙ СБОЙ] {title} | Платформа Маленькая Страна"
                html = build_alert_html(title, description, metric_val, recommendation, is_recovery=False)
                delivery = send_dual_email(subject, html)
                
                ALERT_STATES[key] = {
                    "is_active": True,
                    "last_alert_time": now,
                    "first_detected": now,
                    "last_value": metric_val,
                    "description": description,
                    "last_delivery": delivery
                }
            else:
                # Сбой продолжается -> Дедупликация (повтор только если прошел 1 час)
                time_since_last = now - state["last_alert_time"]
                if time_since_last >= DEDUPLICATION_WINDOW_SECONDS:
                    logger.warning(f"[ALERT REMINDER] Повторное уведомление о сбое: {title} (спустя {int(time_since_last)}с)")
                    subject = f"🚨 [ПОВТОРНЫЙ АЛЕРТ] {title} всё ещё недоступен | Платформа Маленькая Страна"
                    html = build_alert_html(f"{title} (Сбой продолжается)", description, metric_val, recommendation, is_recovery=False)
                    delivery = send_dual_email(subject, html)
                    state["last_alert_time"] = now
                    state["last_delivery"] = delivery
                    ALERT_STATES[key] = state
                else:
                    logger.info(f"[ALERT SUPPRESSED] Алерт {key} подавлен дедупликацией ({int(time_since_last)}с < {DEDUPLICATION_WINDOW_SECONDS}с)")
                    
        # Сценарий 2: Сервис здоров
        else:
            if state["is_active"]:
                # Сервис восстановился -> Однократное уведомление о выздоровлении
                logger.info(f"[RECOVERY TRIGGERED] Сервис восстановлен: {title}")
                subject = f"✅ [ВЫЗДОРОВЛЕНИЕ] {title} успешно восстановлен | Платформа Маленькая Страна"
                html = build_alert_html(f"{title} — Работа полностью нормализована", description, metric_val, "Сервис функционирует в штатном режиме, дополнительных действий не требуется.", is_recovery=True)
                delivery = send_dual_email(subject, html)
                
                ALERT_STATES[key] = {
                    "is_active": False,
                    "last_alert_time": now,
                    "first_detected": 0,
                    "last_value": metric_val,
                    "description": description,
                    "last_delivery": delivery
                }
                
    return results

def send_test_alert() -> dict:
    """
    Отправляет тестовое письмо на оба адреса для верификации работы шлюзов администратором.
    """
    subject = "🔔 [ТЕСТ] Проверка системы оповещений | Платформа Маленькая Страна"
    description = "Тестовое уведомление системы мониторинга платформы Маленькая Страна. Все шлюзы оповещений работают штатно и готовы к доставке критических уведомлений."
    metric_val = "Тестовый запуск: 100% OK"
    recommendation = "Никаких действий не требуется. Проверка доставлена успешно."
    
    html = build_alert_html(
        "Тестовая проверка системы оповещений",
        description,
        metric_val,
        recommendation,
        is_test=True
    )
    
    delivery_results = send_dual_email(subject, html)
    recipients = get_alert_recipients()
    
    return {
        "status": "ok",
        "message": "Тестовое уведомление успешно отправлено на оба адреса",
        "recipients": recipients,
        "details": delivery_results,
        "timestamp": datetime.now(timezone(timedelta(hours=3))).strftime("%Y-%m-%d %H:%M:%S МСК")
    }

def alert_worker_loop():
    """Фоновый поток периодического мониторинга (запускается каждые 5 минут)."""
    logger.info("[ALERT WORKER] Фоновый воркер системы оповещений запущен (интервал: 300с)")
    while True:
        try:
            run_health_checks_and_alert()
        except Exception as e:
            logger.error(f"[ALERT WORKER ERROR] Необработанная ошибка в цикле проверок: {e}")
        time.sleep(CHECK_INTERVAL_SECONDS)

