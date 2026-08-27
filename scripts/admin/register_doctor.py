#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
Скрипт онбординга и регистрации нового врача / специалиста клиники
Проект: ИИ-Консультант «Маленькая Страна» (цмз.site)
=============================================================================
"""

import sys
import os
import re
import string
import secrets
import argparse
import bcrypt

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import database
import notification_service

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def generate_secure_password(length: int = 12) -> str:
    """Генерация криптографически стойкого пароля"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pwd)
                and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd)
                and any(c in "!@#$%^&*" for c in pwd)):
            return pwd

def register_doctor(full_name: str, specialty: str, email: str, license_number: str = None, phone: str = None) -> dict:
    """
    Регистрирует врача в базе данных, генерирует доступы и отправляет email.
    """
    database.init_db()
    
    full_name = full_name.strip()
    specialty = specialty.strip()
    email = email.strip().lower()

    if not EMAIL_REGEX.match(email):
        raise ValueError(f"Некорректный формат адреса электронной почты: '{email}'")

    # Проверка уникальности email
    existing = database.get_doctor_by_email(email)
    if existing:
        raise ValueError(f"Врач с адресом электронной почты '{email}' уже зарегистрирован (ID: {existing.get('id')}).")

    if not license_number:
        license_number = f"DOC-{secrets.token_hex(3).upper()}"
    else:
        license_number = license_number.strip()

    # Генерация пароля и хэширование
    temp_password = generate_secure_password(12)
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), salt).decode('utf-8')

    # Создание записи в БД
    doctor = database.create_doctor(
        full_name=full_name,
        specialty=specialty,
        license_number=license_number,
        is_verified=True,
        email=email,
        password_hash=password_hash,
        role="DOCTOR"
    )

    # Отправка email с поддержкой каскада
    print(f"\n[EMAIL] Отправка учетных данных на '{email}'...")
    email_sent = False
    transport_used = "failed"
    try:
        email_res = notification_service.send_doctor_onboarding_email(
            doctor_email=email,
            full_name=full_name,
            temp_password=temp_password,
            specialty=specialty,
            return_details=True
        )
        if isinstance(email_res, tuple):
            email_sent, transport_used = email_res
        else:
            email_sent = bool(email_res)
            transport_used = "smtp" if email_sent else "failed"
    except Exception as e:
        print(f"[EMAIL ERROR] Ошибка при отправке письма: {e}")

    return {
        "doctor": doctor,
        "temporary_password": temp_password,
        "email_sent": email_sent,
        "transport_used": transport_used
    }

def main():
    parser = argparse.ArgumentParser(
        description="Регистрация и онбординг специалистов/врачей ЦМЗ «Маленькая Страна»"
    )
    parser.add_argument("--name", type=str, help="Полное ФИО врача (например: Сергеева Ольга Дмитриевна)")
    parser.add_argument("--specialty", type=str, help="Специализация (например: Детский клинический психолог)")
    parser.add_argument("--email", type=str, help="Электронная почта для отправки реквизитов")
    parser.add_argument("--license", type=str, default=None, help="Номер лицензии (опционально, по умолчанию автогенерация DOC-XXXXXX)")
    parser.add_argument("--phone", type=str, default=None, help="Контактный номер телефона (опционально)")

    args = parser.parse_args()

    full_name = args.name
    specialty = args.specialty
    email = args.email
    license_num = args.license
    phone = args.phone

    # Если параметры не переданы через CLI, интерактивный режим
    if not (full_name and specialty and email):
        print("============================================================")
        print("🩺 ОНБОРДИНГ СПЕЦИАЛИСТОВ КЛИНИКИ «МАЛЕНЬКАЯ СТРАНА»")
        print("============================================================")
        if not full_name:
            full_name = input("Введите ФИО специалиста: ").strip()
        if not specialty:
            specialty = input("Введите специализацию: ").strip()
        if not email:
            email = input("Введите Email для отправки доступов: ").strip()
        if not license_num:
            lic_input = input("Номер лицензии (нажмите Enter для автогенерации): ").strip()
            license_num = lic_input if lic_input else None
        if not phone:
            phone_input = input("Номер телефона (нажмите Enter, чтобы пропустить): ").strip()
            phone = phone_input if phone_input else None

    if not full_name or not specialty or not email:
        print("\n❌ Ошибка: ФИО, Специализация и Email являются обязательными полями!")
        sys.exit(1)

    try:
        result = register_doctor(
            full_name=full_name,
            specialty=specialty,
            email=email,
            license_number=license_num,
            phone=phone
        )

        doc = result["doctor"]
        temp_pass = result["temporary_password"]
        email_sent = result["email_sent"]
        transport_used = result.get("transport_used", "smtp" if email_sent else "failed")

        print("\n" + "=" * 60)
        print("🎉 СПЕЦИАЛИСТ УСПЕШНО ЗАРЕГИСТРИРОВАН В СИСТЕМЕ!")
        print("=" * 60)
        print(f"👤 ФИО:               {doc.get('full_name')}")
        print(f"🩺 Специализация:     {doc.get('specialty')}")
        print(f"📧 Логин / Email:     {doc.get('email')}")
        print(f"🔑 Временный пароль:  {temp_pass}")
        print(f"📜 Номер лицензии:    {doc.get('license_number')}")
        print(f"🆔 ID в базе данных:  {doc.get('id')}")
        print(f"🔗 Ссылка для входа:  https://xn--g1aj3a.site/#doctor (https://цмз.site/#doctor)")
        print("-" * 60)
        if email_sent:
            channel_name = "Yandex SMTP (SSL 465)" if transport_used == "smtp" else "UniSender API (HTTPS fallback)"
            print(f"✉️ Статус уведомления: Письмо с доступом отправлено через {channel_name} и продублировано на ящик клиники.")
        else:
            print("⚠️ Статус уведомления: Не удалось отправить письмо через SMTP / UniSender. Передайте пароль врачу вручную.")
        print("=" * 60 + "\n")

    except Exception as err:
        print(f"\n❌ Ошибка регистрации: {err}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
