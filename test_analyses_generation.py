import unittest
import uuid
from rag import _deterministic_extract_analyses, _post_process_analyses
from analyses_generator import generate_analyses_docx
from database import (
    init_db, save_patient_analyses_doc, get_patient_analyses_docs,
    get_patient_analyses_doc_by_id, delete_patient_analyses_doc
)

class TestAnalysesGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_deterministic_extract_and_post_process(self):
        raw_text = """
        Дата осмотра: 12.02.2026
        Клинический анализ:
        Гемоглобин: 110 г/л (норма 120-140)
        Ферритин: 18 нг/мл (норма 30-100)
        
        Дата повторного осмотра: 15.05.2026
        Гемоглобин: 128 г/л (норма 120-140)
        Ферритин: 42 нг/мл (норма 30-100)
        Витамин D: 45 нг/мл (норма 30-100)
        """

        extracted = _deterministic_extract_analyses(raw_text)
        self.assertGreaterEqual(len(extracted), 4)

        processed = _post_process_analyses(extracted)
        self.assertEqual(len(processed), len(extracted))

        # Check dynamics on repeated hemoglobin
        hgb_items = [x for x in processed if "Гемоглобин" in x["parameter"]]
        self.assertEqual(len(hgb_items), 2)
        self.assertTrue(hgb_items[0]["is_repeated"])
        self.assertTrue(hgb_items[1]["is_repeated"])
        self.assertEqual(hgb_items[1]["dynamics"], "↑")

    def test_generate_analyses_docx(self):
        sample_data = [
            {
                "date": "2026-02-12",
                "test_name": "Клинический анализ крови (Гемоглобин)",
                "parameter": "Гемоглобин",
                "value": "110 г/л",
                "norm": "120-140 г/л",
                "deviation": "Ниже нормы",
                "is_out_of_norm": True,
                "is_repeated": True,
                "dynamics": "",
                "comment": "Легкая анемизация"
            },
            {
                "date": "2026-05-15",
                "test_name": "Клинический анализ крови (Гемоглобин)",
                "parameter": "Гемоглобин",
                "value": "128 г/л",
                "norm": "120-140 г/л",
                "deviation": "В норме",
                "is_out_of_norm": False,
                "is_repeated": True,
                "dynamics": "↑",
                "comment": "Положительная динамика"
            }
        ]

        docx_bytes = generate_analyses_docx(
            patient_name="Пациент Тестовый",
            analyses_data=sample_data,
            doctor_name="Д-р Волкова А.С."
        )

        self.assertIsInstance(docx_bytes, bytes)
        self.assertGreater(len(docx_bytes), 10000)
        # DOCX files are zip archives starting with PK
        self.assertTrue(docx_bytes.startswith(b"PK"))

    def test_database_analyses_crud(self):
        folder_id = f"disk:/test_patient_{uuid.uuid4().hex[:6]}"
        doctor_id = 1
        analyses_data = [
            {"date": "2026-01-10", "test_name": "Ферритин", "value": "22 нг/мл", "is_out_of_norm": True}
        ]

        # 1. Save
        doc = save_patient_analyses_doc(folder_id, doctor_id, analyses_data)
        doc_id = doc["id"]
        self.assertIsNotNone(doc_id)
        self.assertEqual(doc["patient_folder_id"], folder_id)

        # 2. Get list
        docs_list = get_patient_analyses_docs(folder_id, doctor_id)
        self.assertTrue(any(d["id"] == doc_id for d in docs_list))

        # 3. Get by ID
        fetched = get_patient_analyses_doc_by_id(doc_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["patient_folder_id"], folder_id)
        self.assertEqual(len(fetched["analyses_data"]), 1)

        # 4. Delete
        delete_patient_analyses_doc(doc_id)
        deleted = get_patient_analyses_doc_by_id(doc_id)
        self.assertIsNone(deleted)

if __name__ == "__main__":
    unittest.main()
