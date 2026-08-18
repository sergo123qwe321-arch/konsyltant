import unittest
import uuid
import sqlite3
from datetime import datetime, timedelta, timezone
import database
from database import (
    init_db,
    create_doctor,
    get_doctor_by_id,
    verify_doctor,
    create_share_grant,
    validate_share_grant,
    get_connection,
    execute_query
)

class TestDoctorSharingSchema(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_doctor_creation_and_verification(self):
        """Проверка создания профиля врача, получения по ID и переключения статуса верификации."""
        unique_lic = f"LIC-{uuid.uuid4().hex[:8]}"
        doc = create_doctor(
            full_name="Иван Сергеевич Павлов",
            specialty="Детский невролог",
            license_number=unique_lic
        )
        
        self.assertIsNotNone(doc)
        self.assertIn("id", doc)
        self.assertEqual(doc["full_name"], "Иван Сергеевич Павлов")
        self.assertEqual(doc["specialty"], "Детский невролог")
        self.assertEqual(doc["license_number"], unique_lic)
        self.assertFalse(doc["is_verified"])
        
        # Получение по ID
        fetched = get_doctor_by_id(doc["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], doc["id"])
        self.assertEqual(fetched["license_number"], unique_lic)
        self.assertFalse(fetched["is_verified"])
        
        # Верификация доктора администратором
        verified = verify_doctor(doc["id"])
        self.assertTrue(verified)
        
        # Повторная проверка статуса
        fetched_updated = get_doctor_by_id(doc["id"])
        self.assertTrue(fetched_updated["is_verified"])
        
        # Проверка несуществующего доктора
        self.assertIsNone(get_doctor_by_id(9999999))
        self.assertFalse(verify_doctor(9999999))

    def test_02_share_grant_creation_and_validation(self):
        """Проверка создания и успешной валидации временного токена доступа (Share Grant)."""
        unique_lic = f"LIC-{uuid.uuid4().hex[:8]}"
        doc = create_doctor(
            full_name="Елена Николаевна Соколова",
            specialty="Логопед-дефектолог",
            license_number=unique_lic
        )
        
        folder_id = f"folder_{uuid.uuid4().hex[:10]}"
        share_token = create_share_grant(
            patient_folder_id=folder_id,
            doctor_id=doc["id"],
            ttl_hours=48
        )
        
        self.assertIsInstance(share_token, str)
        self.assertTrue(share_token.startswith("grant_"))
        
        # Валидация активного гранта
        grant_data = validate_share_grant(share_token)
        self.assertIsNotNone(grant_data)
        self.assertEqual(grant_data["patient_folder_id"], folder_id)
        self.assertEqual(grant_data["doctor_id"], doc["id"])
        self.assertEqual(grant_data["share_token"], share_token)
        self.assertTrue(grant_data["is_active"])
        self.assertIn("expires_at", grant_data)

    def test_03_expired_inactive_and_invalid_share_grants(self):
        """Проверка отклонения невалидных, истекших и деактивированных токенов шеринга."""
        # 1. Несуществующий токен
        self.assertIsNone(validate_share_grant("invalid_fake_token_12345"))
        self.assertIsNone(validate_share_grant(""))
        self.assertIsNone(validate_share_grant(None))
        
        # 2. Истекший токен (создаем с отрицательным TTL)
        unique_lic = f"LIC-{uuid.uuid4().hex[:8]}"
        doc = create_doctor(
            full_name="Дмитрий Алексеевич Орлов",
            specialty="Клинический психолог",
            license_number=unique_lic
        )
        folder_id = f"folder_{uuid.uuid4().hex[:10]}"
        expired_token = create_share_grant(
            patient_folder_id=folder_id,
            doctor_id=doc["id"],
            ttl_hours=-5  # Истек 5 часов назад
        )
        self.assertIsNone(validate_share_grant(expired_token), "Истекший токен должен возвращать None")
        
        # 3. Деактивированный токен (is_active = 0 / FALSE)
        active_token = create_share_grant(
            patient_folder_id=folder_id,
            doctor_id=doc["id"],
            ttl_hours=24
        )
        # Убедимся, что он валиден
        self.assertIsNotNone(validate_share_grant(active_token))
        
        # Принудительно деактивируем
        conn = get_connection()
        cursor = conn.cursor()
        val_inactive = False if (database.DATABASE_URL and database.psycopg2) else 0
        execute_query(cursor, "UPDATE patient_share_grants SET is_active = ? WHERE share_token = ?", (val_inactive, active_token))
        conn.commit()
        conn.close()
        
        # Теперь валидация должна вернуть None
        self.assertIsNone(validate_share_grant(active_token), "Деактивированный токен должен возвращать None")

if __name__ == "__main__":
    unittest.main()
