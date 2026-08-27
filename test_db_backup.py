import os
import sys
import time
import gzip
import shutil
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from fastapi.testclient import TestClient
from main import app
import database
from security_utils import create_access_token
from scripts.admin.backup_db import (
    create_backup,
    list_backups,
    rotate_backups,
    format_bytes,
    get_db_config
)


class TestDatabaseBackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.init_db()
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({"sub": "admin", "role": "ADMIN", "full_name": "Администратор Клиники"})
        cls.doctor_token = create_access_token({"sub": "15", "doctor_id": 15, "role": "DOCTOR", "full_name": "Д-р Смирнов"})
        cls.patient_token = create_access_token({"sub": "patient_1", "role": "PATIENT", "full_name": "Пациент"})

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="cmz_test_backups_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_backup_creation_and_filename_structure(self):
        """1. Проверка создания сжатого дампа и структуры имени файла"""
        res = create_backup(output_dir=self.test_dir)
        self.assertEqual(res["status"], "ok")
        self.assertFalse(res["dry_run"])
        self.assertTrue(res["filename"].startswith("backup_konsyltant_"))
        self.assertTrue(res["filename"].endswith(".sql.gz"))
        self.assertTrue(os.path.exists(res["filepath"]))
        self.assertGreater(res["size_bytes"], 0)
        self.assertIn("size_human", res)
        self.assertIn("created_at", res)

        # Проверка целостности gzip-архива
        with gzip.open(res["filepath"], "rt", encoding="utf-8", errors="ignore") as f:
            header = f.read(100)
            self.assertGreater(len(header), 0)

    def test_02_backup_rotation_retention_policy(self):
        """2. Проверка политики ротации: удаление устаревших и избыточных бэкапов"""
        now = time.time()
        # Создаем 10 искусственных файлов бэкапов с шагом в 1 день в прошлое
        created_files = []
        for i in range(10):
            ts_str = datetime.fromtimestamp(now - (i * 86400)).strftime("%Y%m%d_%H%M%S")
            fname = f"backup_konsyltant_{ts_str}.sql.gz"
            fpath = os.path.join(self.test_dir, fname)
            with gzip.open(fpath, "wt", encoding="utf-8") as gz:
                gz.write(f"-- Dump #{i}\n")
            # Устанавливаем mtime
            file_mtime = now - (i * 86400)
            os.utime(fpath, (file_mtime, file_mtime))
            created_files.append((fname, file_mtime))

        self.assertEqual(len(list_backups(self.test_dir)), 10)

        # Применяем ротацию: max_backups=5, retention_days=7
        deleted = rotate_backups(self.test_dir, retention_days=7, max_backups=5)
        self.assertEqual(len(deleted), 5)

        remaining = list_backups(self.test_dir)
        self.assertEqual(len(remaining), 5)
        # Самый свежий бэкап остался на первом месте
        self.assertEqual(remaining[0]["filename"], created_files[0][0])

    def test_03_backup_dry_run_mode(self):
        """3. Проверка режима сухого прогона (--dry-run)"""
        res = create_backup(output_dir=self.test_dir, dry_run=True)
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["dry_run"])
        self.assertFalse(os.path.exists(res["filepath"]))
        self.assertEqual(res["size_bytes"], 0)

    def test_04_format_bytes_utility(self):
        """4. Проверка утилиты форматирования размера файлов"""
        self.assertEqual(format_bytes(500), "500 B")
        self.assertEqual(format_bytes(2048), "2.0 KB")
        self.assertEqual(format_bytes(1048576 * 5), "5.0 MB")
        self.assertEqual(format_bytes(1073741824 * 2), "2.00 GB")

    def test_05_admin_backup_api_rbac_and_execution(self):
        """5. Проверка RBAC и вызова API /api/v1/admin/backup и /api/v1/admin/backups"""
        # 5a. Неавторизованный запрос -> 401
        res_unauth = self.client.post("/api/v1/admin/backup")
        self.assertEqual(res_unauth.status_code, 401)
        res_list_unauth = self.client.get("/api/v1/admin/backups")
        self.assertEqual(res_list_unauth.status_code, 401)

        # 5b. Роль PATIENT -> 403
        headers_patient = {"Authorization": f"Bearer {self.patient_token}"}
        res_pat = self.client.post("/api/v1/admin/backup", headers=headers_patient)
        self.assertEqual(res_pat.status_code, 403)
        res_list_pat = self.client.get("/api/v1/admin/backups", headers=headers_patient)
        self.assertEqual(res_list_pat.status_code, 403)

        # 5c. Роль DOCTOR -> 403
        headers_doc = {"Authorization": f"Bearer {self.doctor_token}"}
        res_doc = self.client.post("/api/v1/admin/backup", headers=headers_doc)
        self.assertEqual(res_doc.status_code, 403)
        res_list_doc = self.client.get("/api/v1/admin/backups", headers=headers_doc)
        self.assertEqual(res_list_doc.status_code, 403)

        # 5d. Роль ADMIN -> 200 OK (Создание дампа и получение списка)
        headers_admin = {"Authorization": f"Bearer {self.admin_token}"}
        res_admin = self.client.post(
            "/api/v1/admin/backup",
            json={"retention_days": 7, "max_backups": 7, "dry_run": False},
            headers=headers_admin
        )
        self.assertEqual(res_admin.status_code, 200)
        data_admin = res_admin.json()
        self.assertEqual(data_admin["status"], "ok")
        self.assertIn("backup", data_admin)
        self.assertTrue(data_admin["backup"]["filename"].endswith(".sql.gz"))

        # Получение списка бэкапов через API
        res_list_admin = self.client.get("/api/v1/admin/backups", headers=headers_admin)
        self.assertEqual(res_list_admin.status_code, 200)
        data_list = res_list_admin.json()
        self.assertEqual(data_list["status"], "ok")
        self.assertIsInstance(data_list["backups"], list)
        self.assertGreaterEqual(data_list["total"], 1)

    @patch("database.get_connection")
    @patch("shutil.which", return_value="/usr/bin/pg_dump")
    @patch("scripts.admin.backup_db.get_db_config")
    def test_06_postgres_backup_flow_mock(self, mock_get_cfg, mock_which, mock_get_conn):
        """6. Проверка ветки выполнения PostgreSQL pg_dump с мокированием"""
        mock_get_cfg.return_value = {
            "is_postgres": True,
            "host": "localhost",
            "port": 5432,
            "user": "postgres_user",
            "password": "secret_password",
            "dbname": "konsyltant_pg",
            "sqlite_path": "konsyltant.db"
        }

        from unittest.mock import MagicMock
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        # Мокируем subprocess.Popen для pg_dump
        import io

        mock_proc = MagicMock()
        mock_proc.stdout = io.BytesIO(b"-- Mock PostgreSQL Dump Data --\nCREATE TABLE test ();\n")
        mock_proc.stderr = io.BytesIO(b"")
        mock_proc.wait.return_value = 0

        with patch("subprocess.Popen", return_value=mock_proc):
            res = create_backup(output_dir=self.test_dir)
            self.assertEqual(res["status"], "ok")
            self.assertEqual(res["db_type"], "postgres")
            self.assertTrue(os.path.exists(res["filepath"]))
            self.assertGreater(res["size_bytes"], 0)

            with gzip.open(res["filepath"], "rt", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Mock PostgreSQL Dump Data", content)


if __name__ == "__main__":
    unittest.main()
