import unittest
from fastapi.testclient import TestClient
from main import app
from database import init_db, create_share_grant
from security_utils import create_access_token

client = TestClient(app)

class TestE2EDoctorShareFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        from database import get_connection, execute_query
        conn = get_connection()
        cursor = conn.cursor()
        execute_query(cursor, "DELETE FROM patient_share_grants WHERE patient_folder_id = 'folder_patient_alex_neuro'")
        conn.commit()
        conn.close()

    def test_e2e_full_patient_to_doctor_share_flow(self):
        # 1. Patient Auth
        patient_token = create_access_token(data={
            'sub': 'patient_alex_2026',
            'allowed_folder': 'folder_patient_alex_neuro',
            'role': 'PATIENT'
        })
        self.assertTrue(bool(patient_token))

        # 2. Patient creates share token with 48h TTL
        share_res = client.post(
            '/api/v1/patient/share',
            json={'expires_in_hours': 48},
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        self.assertEqual(share_res.status_code, 200, f'Share creation failed: {share_res.text}')
        share_data = share_res.json()
        self.assertIn('share_token', share_data)
        self.assertIn('expires_at', share_data)
        self.assertIn('share_url', share_data)
        share_token = share_data['share_token']
        self.assertTrue(share_token.startswith('grant_'))

        # 3. Doctor logs in
        doc_login_res = client.post('/api/v1/doctor/login', json={
            'login': 'doc_anna',
            'password': 'doctor123'
        })
        self.assertEqual(doc_login_res.status_code, 200, f'Doctor login failed: {doc_login_res.text}')
        doc_data = doc_login_res.json()
        doc_token = doc_data['access_token']
        self.assertEqual(doc_data['full_name'], 'Анна Сергеевна Волкова')
        self.assertEqual(doc_data['specialty'], 'Ведущий нейропсихолог')

        # 4. Doctor requests records by share_token
        records_res = client.get(
            f'/api/v1/doctor/patient-records/{share_token}',
            headers={'Authorization': f'Bearer {doc_token}'}
        )
        self.assertEqual(records_res.status_code, 200, f'Get patient records failed: {records_res.text}')
        records = records_res.json()
        self.assertEqual(records['status'], 'success')
        self.assertEqual(records['patient_folder_id'], 'folder_patient_alex_neuro')
        self.assertIn('documents', records)
        self.assertGreaterEqual(len(records['documents']), 1)
        self.assertIn('expires_at', records)

        # 5. Invalid and Expired Token Rejection
        invalid_res = client.get(
            '/api/v1/doctor/patient-records/grant_invalid_token_xyz',
            headers={'Authorization': f'Bearer {doc_token}'}
        )
        self.assertEqual(invalid_res.status_code, 403)

        expired_token = create_share_grant('folder_patient_alex_neuro', ttl_hours=-5)
        expired_res = client.get(
            f'/api/v1/doctor/patient-records/{expired_token}',
            headers={'Authorization': f'Bearer {doc_token}'}
        )
        self.assertEqual(expired_res.status_code, 403)

        # 6. Patient role trying to access doctor endpoint
        forbidden_res = client.get(
            f'/api/v1/doctor/patient-records/{share_token}',
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        self.assertEqual(forbidden_res.status_code, 403)

if __name__ == '__main__':
    unittest.main()
