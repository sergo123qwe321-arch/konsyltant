import unittest
from unittest.mock import patch, MagicMock
from rag import (
    OkapiBM25,
    tokenize,
    stem_russian,
    build_patient_context,
    ask_consultant,
    generate_medical_summary,
    PatientContext,
    MAX_DEFAULT_CHARS
)

class TestBM25Retriever(unittest.TestCase):
    """
    Модульные тесты для проверки лексического поиска (BM25 Retriever),
    токенизации, стемминга и интеграции с GigaChat в модуле rag.py.
    """

    def setUp(self):
        self.test_chunks = [
            "--- Файл: осмотр_педиатра.txt ---\nОбщее состояние удовлетворительное, ребенок активен, жалоб нет.",
            "--- Файл: биохимия_лаборатория.pdf ---\nВ исследовании обнаружен редкий медицинский маркер бибуп в количестве 42 мкг/л.",
            "--- Файл: экг_кардиолог.txt ---\nЭКГ: Ритм синусовый, ЧСС 78 в минуту, нормальное положение оси.",
            "--- Файл: протокол_мрт.pdf ---\nПроведено МРТ головного мозга: очаговой и диффузной патологии не обнаружено.",
            "--- Файл: аллергопробы.txt ---\nУстановлена острая аллергия на цитрусовые и пенициллин с выраженной реакцией.",
            "--- Файл: термометрия.txt ---\nУтренняя температура тела 36.6 С, признаков воспаления нет."
        ]
        self.mock_cache = {
            "chunks": self.test_chunks,
            "patient_name": "Тестовый Пациент",
            "file_count": 6
        }

    def test_russian_stemmer(self):
        """Проверка стеммера Портера: сохранение корня и обработка окончаний"""
        self.assertEqual(stem_russian("бибуп"), "бибуп")
        self.assertEqual(stem_russian("бибупа"), "бибуп")
        self.assertEqual(stem_russian("бибупом"), "бибуп")
        self.assertEqual(stem_russian("анализы"), "анализ")
        self.assertEqual(stem_russian("анализах"), "анализ")
        self.assertEqual(stem_russian("аллергия"), "аллерг")
        self.assertEqual(stem_russian("аллергии"), "аллерг")
        self.assertEqual(stem_russian("аллергией"), "аллерг")
        # Короткие медицинские аббревиатуры не должны обрезаться
        self.assertEqual(stem_russian("мрт"), "мрт")
        self.assertEqual(stem_russian("узи"), "узи")
        self.assertEqual(stem_russian("экг"), "экг")

    def test_russian_tokenizer_and_stopwords(self):
        """Проверка токенизатора: удаление стоп-слов, знаков препинания и нормализация"""
        text = "И в документах у него, возможно, обнаружен бибуп!"
        tokens = tokenize(text)
        # Стоп-слова 'и', 'в', 'у', 'него' должны быть отфильтрованы
        self.assertIn("бибуп", tokens)
        self.assertIn("документ", tokens)
        self.assertNotIn("и", tokens)
        self.assertNotIn("в", tokens)
        self.assertNotIn("у", tokens)

    @patch("rag.fetch_yandex_cache_json")
    def test_exact_term_search(self, mock_fetch):
        """Точный поиск термина (например, 'бибуп')"""
        mock_fetch.return_value = (self.mock_cache, True)

        context = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="бибуп", top_k=1)
        
        self.assertIsInstance(context, str)
        self.assertIn("бибуп", context)
        self.assertIn("--- Файл: биохимия_лаборатория.pdf ---", context)
        self.assertNotIn("протокол_мрт.pdf", context)
        self.assertNotIn("экг_кардиолог.txt", context)

    @patch("rag.fetch_yandex_cache_json")
    def test_word_forms_inflection_search(self, mock_fetch):
        """Поиск по словоформам и грамматическим падежам"""
        mock_fetch.return_value = (self.mock_cache, True)

        # 1. Запрос в падеже 'бибупа' должен находить 'бибуп'
        ctx1 = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="покажи уровень бибупа", top_k=1)
        self.assertIn("--- Файл: биохимия_лаборатория.pdf ---", ctx1)
        self.assertIn("бибуп", ctx1)

        # 2. Запрос 'аллергии' во множественном числе должен находить 'аллергия'
        ctx2 = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="какие у ребенка аллергии?", top_k=1)
        self.assertIn("--- Файл: аллергопробы.txt ---", ctx2)
        self.assertIn("аллергия", ctx2)

    @patch("rag.fetch_yandex_cache_json")
    def test_synonym_expansion_search(self, mock_fetch):
        """Поиск с расширением синонимов (Query Expansion): 'томография' -> 'мрт', 'жар' -> 'температура'"""
        mock_fetch.return_value = (self.mock_cache, True)

        # 'томография' должна через синоним находить чанк с 'МРТ'
        ctx_mrt = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="делали ли ребенку томографию мозга?", top_k=1)
        self.assertIn("--- Файл: протокол_мрт.pdf ---", ctx_mrt)
        self.assertIn("МРТ головного мозга", ctx_mrt)

        # 'жар' или 'лихорадка' должен находить чанк с 'температура'
        ctx_temp = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="был ли сильный жар или лихорадка?", top_k=1)
        self.assertIn("--- Файл: термометрия.txt ---", ctx_temp)
        self.assertIn("температура тела", ctx_temp)

    @patch("rag.fetch_yandex_cache_json")
    def test_empty_and_none_query_behavior(self, mock_fetch):
        """Поведение при пустом запросе, пробелах или None (дефолтный срез)"""
        mock_fetch.return_value = (self.mock_cache, True)

        # Пустой запрос None
        ctx_none, exists_none = build_patient_context(patient_folder="disk:/Тестовый Пациент", query=None)
        self.assertTrue(exists_none)
        self.assertIn("осмотр_педиатра.txt", ctx_none)

        # Пустая строка ""
        ctx_empty, exists_empty = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="")
        self.assertTrue(exists_empty)
        self.assertIn("осмотр_педиатра.txt", ctx_empty)

        # Строка из пробелов
        ctx_spaces, exists_spaces = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="    ")
        self.assertTrue(exists_spaces)
        self.assertIn("осмотр_педиатра.txt", ctx_spaces)

    @patch("rag.fetch_yandex_cache_json")
    def test_context_length_limit(self, mock_fetch):
        """Проверка ограничения максимальной длины контекста (MAX_DEFAULT_CHARS)"""
        # Генерируем 30 больших чанков по 1 000 символов каждый (всего 30 000 символов)
        large_chunks = [
            f"--- Файл: том_{i}.txt ---\n" + ("Текст медицинской карты и подробный анамнез пациента. " * 20)
            for i in range(30)
        ]
        large_cache = {"chunks": large_chunks}
        mock_fetch.return_value = (large_cache, True)

        # Без запроса: дефолтный срез не должен превышать MAX_DEFAULT_CHARS
        context, exists = build_patient_context(patient_folder="disk:/Большой Пациент", query=None)
        self.assertTrue(exists)
        self.assertLessEqual(len(context), MAX_DEFAULT_CHARS + 2000)

        # С запросом и большим top_k: также соблюдается лимит
        context_q, exists_q = build_patient_context(patient_folder="disk:/Большой Пациент", query="анамнез", top_k=25)
        self.assertTrue(exists_q)
        self.assertLessEqual(len(context_q), MAX_DEFAULT_CHARS + 2000)

    @patch("rag.fetch_yandex_cache_json")
    def test_file_headers_preservation(self, mock_fetch):
        """Сохранение мета-заголовков файлов '--- Файл: {path} ---' в отобранных чанках"""
        mock_fetch.return_value = (self.mock_cache, True)

        context, exists = build_patient_context(patient_folder="disk:/Тестовый Пациент", query="бибуп", top_k=1)
        self.assertTrue(exists)
        self.assertTrue(context.startswith("--- Файл: биохимия_лаборатория.pdf ---"))

    @patch("rag.fetch_yandex_cache_json")
    def test_cache_not_exists_and_empty_chunks(self, mock_fetch):
        """Корректная обработка отсутствия кэша или пустых чанков"""
        # Кэш не существует
        mock_fetch.return_value = (None, False)
        ctx, exists = build_patient_context(patient_folder="disk:/Несуществующий Пациент")
        self.assertFalse(exists)
        self.assertEqual(ctx, "")

        # Кэш пустой
        mock_fetch.return_value = ({"chunks": []}, True)
        ctx_empty, exists_empty = build_patient_context(patient_folder="disk:/Пустой Пациент")
        self.assertTrue(exists_empty)
        self.assertIn("В обработанном кэше пока нет содержательного текста", ctx_empty)

    @patch("rag.fetch_yandex_cache_json")
    @patch("rag.get_gigachat_token")
    @patch("rag.requests.post")
    def test_ask_consultant_bm25_integration(self, mock_post, mock_token, mock_fetch):
        """Проверка сквозной передачи запроса пользователя в BM25 через ask_consultant"""
        mock_fetch.return_value = (self.mock_cache, True)
        mock_token.return_value = "fake_jwt_token_123"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Концентрация бибупа составляет 42 мкг/л."}}],
            "usage": {"prompt_tokens": 120, "completion_tokens": 15, "total_tokens": 135}
        }
        mock_post.return_value = mock_resp

        reply = ask_consultant("Какая концентрация маркера бибуп?", "disk:/Тестовый Пациент")
        self.assertEqual(reply, "Концентрация бибупа составляет 42 мкг/л.")

        # Проверяем, что в системный промпт был передан именно релевантный чанк с бибупом
        call_kwargs = mock_post.call_args[1]
        sent_messages = call_kwargs["json"]["messages"]
        system_content = sent_messages[0]["content"]
        self.assertIn("биохимия_лаборатория.pdf", system_content)
        self.assertIn("бибуп в количестве 42 мкг/л", system_content)
        # Нерелевантные чанки (например, ЭКГ) не должны попасть в Top-1 контекст
        self.assertNotIn("экг_кардиолог.txt", system_content)

    @patch("rag.fetch_yandex_cache_json")
    @patch("rag.get_gigachat_token")
    @patch("rag.requests.post")
    def test_generate_medical_summary_limit_integration(self, mock_post, mock_token, mock_fetch):
        """Проверка работы generate_medical_summary с безопасным срезом контекста"""
        mock_fetch.return_value = (self.mock_cache, True)
        mock_token.return_value = "fake_jwt_token_123"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"anamnesis": "Здоров", "diagnoses": [], "contraindications": [], "drug_interactions": [], "recommendations": []}'
                }
            }],
            "usage": {"prompt_tokens": 200, "completion_tokens": 40, "total_tokens": 240}
        }
        mock_post.return_value = mock_resp

        summary_dict, raw_text, exists = generate_medical_summary("disk:/Тестовый Пациент")
        self.assertTrue(exists)
        self.assertIsNotNone(summary_dict)
        self.assertEqual(summary_dict.get("anamnesis"), "Здоров")

if __name__ == "__main__":
    unittest.main()
