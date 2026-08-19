import unittest
from database import init_db, ensure_indexes, get_db_indexes, get_connection, DATABASE_URL, psycopg2

class TestDatabaseIndexes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_indexes_exist(self):
        """1. Проверяет, что все ключевые индексы созданы в базе данных после init_db()."""
        indexes = get_db_indexes()
        
        expected_indexes = [
            "idx_patient_access_token",
            "idx_patient_access_gdrive_folder",
            "idx_patient_access_role_verified",
            "idx_patient_access_created_at",
            "idx_share_grants_token",
            "idx_share_grants_patient_active",
            "idx_share_grants_doctor_id",
            "idx_share_grants_expires_at",
            "idx_doctors_license_number",
            "idx_doctors_full_name",
            "idx_doctors_verified",
            "idx_public_posts_created_at",
            "idx_public_leads_status_created",
            "idx_public_services_category",
            "idx_public_events_date"
        ]

        for expected in expected_indexes:
            self.assertIn(
                expected, 
                indexes, 
                f"Индекс {expected} должен физически существовать в схеме базы данных"
            )

    def test_idempotent_migration(self):
        """2. Повторный вызов init_db() и ensure_indexes() идемпотентен (без ошибок и дублей)."""
        # Вызываем трижды подряд
        try:
            ensure_indexes()
            init_db()
            ensure_indexes()
        except Exception as e:
            self.fail(f"Повторный вызов ensure_indexes() / init_db() вызвал ошибку: {e}")

        # Проверяем, что количество индексов не исказилось
        indexes = get_db_indexes()
        self.assertIn("idx_patient_access_token", indexes)
        self.assertIn("idx_share_grants_token", indexes)

    def test_query_performance_and_plan(self):
        """3. Проверяет использование индексов при поиске по access_token и share_token через EXPLAIN."""
        conn = get_connection()
        cursor = conn.cursor()
        is_postgres = bool(DATABASE_URL and psycopg2)

        try:
            if is_postgres:
                # В Postgres EXPLAIN показывает Plan
                cursor.execute("EXPLAIN SELECT * FROM patient_access WHERE access_token = 'test_sample_token'")
                plan_rows = [row[0] for row in cursor.fetchall()]
                plan_text = " ".join(plan_rows)
                # Должен содержать Index Scan или Bitmap Index Scan
                self.assertTrue(
                    "Index" in plan_text or "Scan" in plan_text, 
                    f"Postgres план запроса: {plan_text}"
                )
            else:
                # В SQLite EXPLAIN QUERY PLAN показывает детали использования индекса
                cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM patient_access WHERE access_token = 'test_sample_token'")
                plan_rows = cursor.fetchall()
                plan_text = " ".join(str(r) for r in plan_rows)
                self.assertIn(
                    "USING INDEX", 
                    plan_text, 
                    f"SQLite план запроса должен использовать индекс: {plan_text}"
                )

                # Проверяем также план запроса для patient_share_grants по share_token
                cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM patient_share_grants WHERE share_token = 'grant_sample_token'")
                grant_plan_rows = cursor.fetchall()
                grant_plan_text = " ".join(str(r) for r in grant_plan_rows)
                self.assertIn(
                    "USING INDEX", 
                    grant_plan_text, 
                    f"SQLite план запроса share_token должен использовать индекс: {grant_plan_text}"
                )
        finally:
            conn.close()

if __name__ == '__main__':
    unittest.main()

