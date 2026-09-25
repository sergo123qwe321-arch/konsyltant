import os
import json
import unittest
from unittest.mock import patch, MagicMock

from folder_watcher import (
    get_all_yandex_disk_files,
    build_and_upload_folder_cache,
    upload_json_to_yandex_disk
)

class TestRecursiveETL(unittest.TestCase):

    def test_01_recursive_traversal_collects_subfolders_and_relpaths(self):
        """1. Проверка рекурсивного спуска по подпапкам с вычислением относительных путей."""
        def mock_yandex_resources(url, headers=None, params=None, timeout=None):
            path = params.get("path", "")
            mock_res = MagicMock()
            mock_res.status_code = 200

            if path == "disk:/Тест Пациент":
                mock_res.json.return_value = {
                    "_embedded": {
                        "items": [
                            {"name": "выписка.docx", "type": "file", "path": "disk:/Тест Пациент/выписка.docx", "size": 1024, "modified": "2026-09-01T10:00:00Z"},
                            {"name": "допфайлы", "type": "dir", "path": "disk:/Тест Пациент/допфайлы"},
                            {"name": "НЭК", "type": "dir", "path": "disk:/Тест Пациент/НЭК"},
                            {"name": "_cache.json", "type": "file", "path": "disk:/Тест Пациент/_cache.json"}
                        ],
                        "total": 4
                    }
                }
            elif path == "disk:/Тест Пациент/допфайлы":
                mock_res.json.return_value = {
                    "_embedded": {
                        "items": [
                            {"name": "скан1.jpg", "type": "file", "path": "disk:/Тест Пациент/допфайлы/скан1.jpg", "size": 2048, "modified": "2026-09-02T10:00:00Z"},
                            {"name": "скан2.png", "type": "file", "path": "disk:/Тест Пациент/допфайлы/скан2.png", "size": 4096, "modified": "2026-09-02T10:05:00Z"}
                        ],
                        "total": 2
                    }
                }
            elif path == "disk:/Тест Пациент/НЭК":
                mock_res.json.return_value = {
                    "_embedded": {
                        "items": [
                            {"name": "Архив", "type": "dir", "path": "disk:/Тест Пациент/НЭК/Архив"},
                            {"name": "диагностика.docx", "type": "file", "path": "disk:/Тест Пациент/НЭК/диагностика.docx", "size": 512, "modified": "2026-09-03T10:00:00Z"}
                        ],
                        "total": 2
                    }
                }
            elif path == "disk:/Тест Пациент/НЭК/Архив":
                mock_res.json.return_value = {
                    "_embedded": {
                        "items": [
                            {"name": "старое.txt", "type": "file", "path": "disk:/Тест Пациент/НЭК/Архив/старое.txt", "size": 128, "modified": "2026-09-04T10:00:00Z"}
                        ],
                        "total": 1
                    }
                }
            else:
                mock_res.json.return_value = {"_embedded": {"items": [], "total": 0}}
            return mock_res

        with patch("folder_watcher.requests.get", side_effect=mock_yandex_resources), \
             patch("folder_watcher.YANDEX_DISK_TOKEN", "fake_token"):
            files, subdirs = get_all_yandex_disk_files("disk:/Тест Пациент")

            self.assertEqual(subdirs, 3)  # допфайлы, НЭК, НЭК/Архив
            rel_paths = [f["relative_path"] for f in files]
            self.assertIn("выписка.docx", rel_paths)
            self.assertIn("допфайлы/скан1.jpg", rel_paths)
            self.assertIn("допфайлы/скан2.png", rel_paths)
            self.assertIn("НЭК/диагностика.docx", rel_paths)
            self.assertIn("НЭК/Архив/старое.txt", rel_paths)
            # Файлы на '_' не должны попадать
            self.assertNotIn("_cache.json", rel_paths)
            self.assertEqual(len(files), 5)

    def test_02_new_cache_schema_structure(self):
        """2. Проверка новой схемы кэша: наличие 'files' со структурой и плоской проекции 'chunks'."""
        mock_files = [
            {"relative_path": "doc.txt", "name": "doc.txt", "path": "disk:/P/doc.txt", "size": 100, "modified": "2026-09-01T12:00:00Z", "mime_type": "text/plain", "file": None}
        ]

        uploaded_payload = {}
        def mock_upload(path, payload):
            nonlocal uploaded_payload
            uploaded_payload = payload
            return True

        with patch("folder_watcher.get_all_yandex_disk_files", return_value=(mock_files, 0)), \
             patch("folder_watcher.download_yandex_file_bytes", side_effect=[b"", "Тестовый медицинский диагноз".encode('utf-8')]), \
             patch("folder_watcher.upload_json_to_yandex_disk", side_effect=mock_upload), \
             patch("folder_watcher.publish_yandex_disk_resource", return_value="https://disk.yandex.ru/d/test"), \
             patch("folder_watcher.save_etl_metric"):
            
            build_and_upload_folder_cache("disk:/P", "Пациент Тест")

            self.assertIn("patient_folder", uploaded_payload)
            self.assertIn("last_updated", uploaded_payload)
            self.assertIn("files", uploaded_payload)
            self.assertIn("chunks", uploaded_payload)

            self.assertIn("doc.txt", uploaded_payload["files"])
            file_meta = uploaded_payload["files"]["doc.txt"]
            self.assertEqual(file_meta["modified"], "2026-09-01T12:00:00Z")
            self.assertEqual(file_meta["size"], 100)
            self.assertTrue(len(file_meta["chunks"]) > 0)
            self.assertIn("--- Файл: doc.txt ---", file_meta["chunks"][0])
            # Плоская проекция содержит те же чанки
            self.assertEqual(uploaded_payload["chunks"], file_meta["chunks"])

    def test_03_differential_sync_skips_unchanged_and_deletes_removed(self):
        """3. Дифференциальная синхронизация: пропуск неизмененных файлов и удаление отсутствующих."""
        existing_cache = {
            "patient_folder": "Пациент Тест",
            "last_updated": "2026-09-01T00:00:00Z",
            "files": {
                "unchanged.txt": {
                    "modified": "2026-09-01T12:00:00Z",
                    "size": 200,
                    "chunks": ["--- Файл: unchanged.txt ---\nСтарый неизмененный чанк"]
                },
                "deleted.txt": {
                    "modified": "2026-08-30T10:00:00Z",
                    "size": 50,
                    "chunks": ["--- Файл: deleted.txt ---\nЧанк удаленного файла"]
                }
            },
            "chunks": [
                "--- Файл: unchanged.txt ---\nСтарый неизмененный чанк",
                "--- Файл: deleted.txt ---\nЧанк удаленного файла"
            ]
        }

        # Текущее состояние на Диске: unchanged.txt остался, deleted.txt удален, new_scan.jpg добавлен
        current_disk_files = [
            {"relative_path": "unchanged.txt", "name": "unchanged.txt", "path": "disk:/P/unchanged.txt", "size": 200, "modified": "2026-09-01T12:00:00Z", "mime_type": "text/plain"},
            {"relative_path": "допфайлы/new_scan.jpg", "name": "new_scan.jpg", "path": "disk:/P/допфайлы/new_scan.jpg", "size": 500, "modified": "2026-09-25T10:00:00Z", "mime_type": "image/jpeg"}
        ]

        uploaded_payload = {}
        def mock_upload(path, payload):
            nonlocal uploaded_payload
            uploaded_payload = payload
            return True

        download_calls = []
        def mock_download(path, direct_url=None):
            download_calls.append(path)
            if "cache.json" in path:
                return json.dumps(existing_cache).encode('utf-8')
            return "Новый распознанный текст со скана".encode('utf-8')

        with patch("folder_watcher.get_all_yandex_disk_files", return_value=(current_disk_files, 1)), \
             patch("folder_watcher.download_yandex_file_bytes", side_effect=mock_download), \
             patch("folder_watcher.parse_document_bytes", return_value="Распознанный текст со скана"), \
             patch("folder_watcher.upload_json_to_yandex_disk", side_effect=mock_upload), \
             patch("folder_watcher.publish_yandex_disk_resource", return_value="https://disk.yandex.ru/d/test"), \
             patch("folder_watcher.save_etl_metric"):

            build_and_upload_folder_cache("disk:/P", "Пациент Тест")

            # unchanged.txt НЕ должен скачиваться повторно!
            self.assertNotIn("disk:/P/unchanged.txt", download_calls)
            # new_scan.jpg должен быть скачан
            self.assertIn("disk:/P/допфайлы/new_scan.jpg", download_calls)

            # deleted.txt удален из files и chunks
            self.assertNotIn("deleted.txt", uploaded_payload["files"])
            # unchanged.txt сохранен со своими прежними чанками
            self.assertIn("unchanged.txt", uploaded_payload["files"])
            self.assertEqual(uploaded_payload["files"]["unchanged.txt"]["chunks"], existing_cache["files"]["unchanged.txt"]["chunks"])
            # new_scan.jpg добавлен
            self.assertIn("допфайлы/new_scan.jpg", uploaded_payload["files"])
            # Плоская проекция объединяет оба файла
            self.assertEqual(len(uploaded_payload["chunks"]), 2)

    def test_04_skip_reupload_when_no_changes(self):
        """4. Полный пропуск пересборки/загрузки, если файлы на Диске совпадают с кэшем."""
        existing_cache = {
            "patient_folder": "Пациент Тест",
            "last_updated": "2026-09-01T00:00:00Z",
            "files": {
                "file1.txt": {"modified": "2026-09-01T10:00:00Z", "size": 100, "chunks": ["Чанк 1"]}
            },
            "chunks": ["Чанк 1"]
        }
        current_disk_files = [
            {"relative_path": "file1.txt", "name": "file1.txt", "path": "disk:/P/file1.txt", "size": 100, "modified": "2026-09-01T10:00:00Z"}
        ]

        with patch("folder_watcher.get_all_yandex_disk_files", return_value=(current_disk_files, 0)), \
             patch("folder_watcher.download_yandex_file_bytes", return_value=json.dumps(existing_cache).encode('utf-8')), \
             patch("folder_watcher.upload_json_to_yandex_disk") as mock_upload, \
             patch("folder_watcher.publish_yandex_disk_resource", return_value="https://disk.yandex.ru/d/test"):

            res = build_and_upload_folder_cache("disk:/P", "Пациент Тест")
            # Загрузка JSON на Диск не должна вызываться
            mock_upload.assert_not_called()
            self.assertEqual(res, "https://disk.yandex.ru/d/test")

    def test_05_legacy_cache_migration(self):
        """5. Миграция устаревшего кэша (где нет поля 'files')."""
        legacy_cache = {
            "patient_folder": "Пациент Тест",
            "last_updated": "2026-09-01T00:00:00Z",
            "chunks": ["Старый чанк без структуры"]
        }
        current_disk_files = [
            {"relative_path": "file1.txt", "name": "file1.txt", "path": "disk:/P/file1.txt", "size": 150, "modified": "2026-09-01T10:00:00Z", "mime_type": "text/plain"}
        ]

        uploaded_payload = {}
        def mock_upload(path, payload):
            nonlocal uploaded_payload
            uploaded_payload = payload
            return True

        with patch("folder_watcher.get_all_yandex_disk_files", return_value=(current_disk_files, 0)), \
             patch("folder_watcher.download_yandex_file_bytes", side_effect=[json.dumps(legacy_cache).encode('utf-8'), "Текст файла".encode('utf-8')]), \
             patch("folder_watcher.parse_document_bytes", return_value="Текст файла"), \
             patch("folder_watcher.upload_json_to_yandex_disk", side_effect=mock_upload), \
             patch("folder_watcher.publish_yandex_disk_resource", return_value="https://disk.yandex.ru/d/test"), \
             patch("folder_watcher.save_etl_metric"):

            build_and_upload_folder_cache("disk:/P", "Пациент Тест")

            self.assertIn("files", uploaded_payload)
            self.assertIn("file1.txt", uploaded_payload["files"])
            self.assertEqual(uploaded_payload["files"]["file1.txt"]["size"], 150)

if __name__ == '__main__':
    unittest.main()
