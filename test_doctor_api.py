import unittest
from fastapi.testclient import TestClient
from main import app
from database import init_db, create_doctor, create_share_grant
from security_utils import create_access_token

client = TestClient(app)

class TestDoctorDataSharingAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        from database import get_connection, execute_query
        conn = get_connection()
        cursor = conn.cursor()
        execute_query(cursor, "DELETE FROM patient_share_grants WHERE patient_folder_id IN ('folder_patient_vault_777', 'folder_speech_patient_888')")
        conn.commit()
        conn.close()

    def test_01_doctor_login_success(self):
        response = client.post('/api/v1/doctor/login', json={
            'login': 'doc_anna',
            'password': 'doctor123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access_token', data)
        self.assertEqual(data['token_type'], 'bearer')
        self.assertIn('doctor_id', data)
        self.assertEqual(data['full_name'], 'Анна Сергеевна Волкова')
        self.assertEqual(data['specialty'], 'Ведущий нейропсихолог')

    def test_02_doctor_login_invalid_credentials(self):
        response = client.post('/api/v1/doctor/login', json={
            'login': 'doc_anna',
            'password': 'wrong_password_xyz'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('Неверный логин или пароль', response.json()['detail'])

        response_fake = client.post('/api/v1/doctor/login', json={
            'login': 'non_existent_doctor',
            'password': 'doctor123'
        })
        self.assertEqual(response_fake.status_code, 401)

    def test_03_patient_creates_share_grant(self):
        patient_token = create_access_token(data={
            'sub': 'patient_test_001',
            'allowed_folder': 'folder_patient_vault_777',
            'role': 'PATIENT'
        })

        response = client.post(
            '/api/v1/patient/share',
            json={'expires_in_hours': 48},
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('share_token', data)
        self.assertTrue(data['share_token'].startswith('grant_'))
        self.assertIn('expires_at', data)
        self.assertIn('share_url', data)
        self.assertIn(data['share_token'], data['share_url'])

    def test_04_doctor_queries_patient_records_success(self):
        doc_login_res = client.post('/api/v1/doctor/login', json={
            'login': 'doc_mikhail',
            'password': 'doctor123'
        })
        self.assertEqual(doc_login_res.status_code, 200)
        doc_token = doc_login_res.json()['access_token']
        doc_id = doc_login_res.json()['doctor_id']

        patient_token = create_access_token(data={
            'sub': 'patient_test_002',
            'allowed_folder': 'folder_speech_patient_888',
            'role': 'PATIENT'
        })
        share_res = client.post(
            '/api/v1/patient/share',
            json={'expires_in_hours': 24, 'doctor_id': doc_id},
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        self.assertEqual(share_res.status_code, 200)
        share_token = share_res.json()['share_token']

        records_res = client.get(
            f'/api/v1/doctor/patient-records/{share_token}',
            headers={'Authorization': f'Bearer {doc_token}'}
        )
        self.assertEqual(records_res.status_code, 200)
        records_data = records_res.json()
        self.assertEqual(records_data['status'], 'success')
        self.assertEqual(records_data['patient_folder_id'], 'folder_speech_patient_888')
        self.assertIn('documents', records_data)
        self.assertIsInstance(records_data['documents'], list)
        self.assertIn('doctor', records_data)

    def test_05_rejection_of_expired_and_invalid_tokens(self):
        doc_login_res = client.post('/api/v1/doctor/login', json={
            'login': 'doc_anna',
            'password': 'doctor123'
        })
        doc_token = doc_login_res.json()['access_token']

        res_invalid = client.get(
            '/api/v1/doctor/patient-records/invalid_grant_token_9999',
            headers={'Authorization': f'Bearer {doc_token}'}
        )
        self.assertEqual(res_invalid.status_code, 403)

        expired_token = create_share_grant('folder_test_expired', ttl_hours=-10)
        res_expired = client.get(
            f'/api/v1/doctor/patient-records/{expired_token}',
            headers={'Authorization': f'Bearer {doc_token}'}
        )
        self.assertEqual(res_expired.status_code, 403)

    def test_06_rbacs_role_enforcement(self):
        res_no_auth = client.get('/api/v1/doctor/patient-records/grant_dummy_123')
        self.assertEqual(res_no_auth.status_code, 401)

        patient_token = create_access_token(data={
            'sub': 'patient_imposter',
            'allowed_folder': 'folder_x',
            'role': 'PATIENT'
        })
        res_patient_forbidden = client.get(
            '/api/v1/doctor/patient-records/grant_dummy_123',
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        self.assertEqual(res_patient_forbidden.status_code, 403)
        self.assertIn('требуются права врача', res_patient_forbidden.json()['detail'])

if __name__ == '__main__':
    unittest.main()
