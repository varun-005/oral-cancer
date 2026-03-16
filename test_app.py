import unittest

from app import app


class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY='test-secret')
        self.client = app.test_client()

    def test_index_route_loads(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Oral Cancer Detection System', response.data)

    def test_result_redirects_without_prediction(self):
        response = self.client.get('/result')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/'))

    def test_predict_without_file_shows_error(self):
        response = self.client.post('/predict', data={}, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No file selected.', response.data)


if __name__ == '__main__':
    unittest.main()