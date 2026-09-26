import unittest
from unittest.mock import patch, MagicMock, call
import folder_watcher
from folder_watcher import (
    get_yandex_disk_folders,
    scan_folders,
    CacheUploadResult
)

class TestScanAllPatients(unittest.TestCase):

    def test_01_filter_system_and_hidden_directories(self):
        """1. get_yandex_disk_folders исключает файлы, а также папки, начинающиеся с '.' или '_'."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_embedded": {
                "items": [
                    {"name": "_system_cache", "type": "dir", "path": "disk:/_system_cache"},
                    {"name": ".trash", "type": "dir", "path": "disk:/.trash"},
                    {"name": "readme.txt", "type": "file", "path": "disk:/readme.txt"},
                    {"name": "Иванов Иван", "type": "dir", "path": "disk:/Иванов Иван"},
                    {"name": "Петров Петр", "type": "dir", "path": "disk:/Петров Петр"},
                    {"name": "_Малышкин_Даня_cache.json", "type": "file", "path": "disk:/_Малышкин_Даня_cache.json"}
                ],
                "total": 6
            }
        }

        with patch("folder_watcher.safe_yandex_request", return_value=mock_response), \
             patch("folder_watcher.YANDEX_DISK_TOKEN", "fake_token"):

            folders = get_yandex_disk_folders("/")
            folder_names = [f["name"] for f in folders]

            # Должны остаться только реальные папки пациентов
            self.assertEqual(folder_names, ["Иванов Иван", "Петров Петр"])
            self.assertEqual(len(folders), 2)

    def test_02_pagination_in_get_yandex_disk_folders(self):
        """2. get_yandex_disk_folders корректно проходит по страницам (offset) при большом числе папок."""
        page1 = MagicMock()
        page1.status_code = 200
        page1.json.return_value = {
            "_embedded": {
                "items": [{"name": f"Пациент {i}", "type": "dir", "path": f"disk:/Пациент {i}"} for i in range(100)],
                "total": 120
            }
        }

        page2 = MagicMock()
        page2.status_code = 200
        page2.json.return_value = {
            "_embedded": {
                "items": [{"name": f"Пациент {i}", "type": "dir", "path": f"disk:/Пациент {i}"} for i in range(100, 120)],
                "total": 120
            }
        }

        with patch("folder_watcher.safe_yandex_request", side_effect=[page1, page2]), \
             patch("folder_watcher.YANDEX_DISK_TOKEN", "fake_token"):

            folders = get_yandex_disk_folders("/")
            self.assertEqual(len(folders), 120)
            self.assertEqual(folders[0]["name"], "Пациент 0")
            self.assertEqual(folders[119]["name"], "Пациент 119")

    def test_03_scan_folders_sequential_full_drain_and_instant_skip(self):
        """3. scan_folders: последовательный обход, исчерпание очереди до остатка 0 и мгновенный пропуск актуальных."""
        mock_folders = [
            {"name": "Большой Пациент", "type": "dir", "path": "disk:/Большой Пациент"},
            {"name": "Актуальный Пациент", "type": "dir", "path": "disk:/Актуальный Пациент"}
        ]

        # Для "Большой Пациент": 3 батча (остаток 40 -> 10 -> 0)
        # Для "Актуальный Пациент": 1 вызов (остаток 0, без изменений)
        batch_results = [
            CacheUploadResult("https://disk.yandex.ru/d/cache1", remaining_files=40),
            CacheUploadResult("https://disk.yandex.ru/d/cache1", remaining_files=10),
            CacheUploadResult("https://disk.yandex.ru/d/cache1", remaining_files=0),
            CacheUploadResult("https://disk.yandex.ru/d/cache2", remaining_files=0)
        ]

        mock_build_cache = MagicMock(side_effect=batch_results)
        mock_sleep = MagicMock()

        with patch("folder_watcher.get_yandex_disk_folders", return_value=mock_folders), \
             patch("folder_watcher.folder_exists", return_value=True), \
             patch("folder_watcher.build_and_upload_folder_cache", mock_build_cache), \
             patch("folder_watcher.time.sleep", mock_sleep), \
             patch("folder_watcher.update_etl_heartbeat"):

            scan_folders()

            # Всего 4 вызова build_and_upload_folder_cache: 3 для первого пациента и 1 для второго
            self.assertEqual(mock_build_cache.call_count, 4)

            # Проверяем, что для "Большой Пациент" было 3 вызова подряд
            calls = mock_build_cache.call_args_list
            self.assertEqual(calls[0][0][1], "Большой Пациент")
            self.assertEqual(calls[1][0][1], "Большой Пациент")
            self.assertEqual(calls[2][0][1], "Большой Пациент")
            # Только после завершения первого наступает очередь второго
            self.assertEqual(calls[3][0][1], "Актуальный Пациент")

            # Пауза между батчами вызывалась ровно 2 раза (между батчами первого пациента)
            self.assertEqual(mock_sleep.call_count, 2)

    def test_04_scan_folders_new_patient_full_drain(self):
        """4. scan_folders: новая папка полностью доиндексируется батчами до 0 перед созданием доступов."""
        mock_folders = [
            {"name": "Новый Пациент", "type": "dir", "path": "disk:/Новый Пациент"}
        ]

        batch_results = [
            CacheUploadResult("https://disk.yandex.ru/d/cache_new", remaining_files=25),
            CacheUploadResult("https://disk.yandex.ru/d/cache_new", remaining_files=0)
        ]

        mock_build_cache = MagicMock(side_effect=batch_results)
        mock_publish = MagicMock(return_value="https://disk.yandex.ru/d/folder_pub")
        mock_create_access = MagicMock(return_value="token_123456789")
        mock_send_email = MagicMock(return_value=True)

        with patch("folder_watcher.get_yandex_disk_folders", return_value=mock_folders), \
             patch("folder_watcher.folder_exists", return_value=False), \
             patch("folder_watcher.build_and_upload_folder_cache", mock_build_cache), \
             patch("folder_watcher.publish_yandex_disk_resource", mock_publish), \
             patch("folder_watcher.create_patient_access", mock_create_access), \
             patch("folder_watcher.NotificationService.send_welcome_email", mock_send_email), \
             patch("folder_watcher.time.sleep"), \
             patch("folder_watcher.update_etl_heartbeat"):

            scan_folders()

            # Должно быть 2 батча до remaining_files == 0
            self.assertEqual(mock_build_cache.call_count, 2)
            # Доступ создается после полной индексации
            mock_create_access.assert_called_once()
            # Email отправляется с публичной ссылкой
            mock_send_email.assert_called_once()

if __name__ == "__main__":
    unittest.main()
