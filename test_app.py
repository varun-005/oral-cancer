import io
import unittest
from unittest.mock import patch

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

    @patch('werkzeug.datastructures.FileStorage.save', autospec=True)
    @patch('app.predict_risk', return_value=42.5)
    @patch('app.preprocess_image', return_value='processed-image')
    def test_predict_with_valid_file_redirects_to_result(self, mock_preprocess, mock_predict_risk, mock_save):
        response = self.client.post(
            '/predict',
            data={'image': (io.BytesIO(b'fake image bytes'), 'oral-sample.jpg')},
            content_type='multipart/form-data'
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/result'))
        mock_preprocess.assert_called_once()
        mock_predict_risk.assert_called_once_with('processed-image')
        self.assertTrue(mock_save.called)

        with self.client.session_transaction() as session_data:
            self.assertEqual(session_data['prediction']['risk_pct'], 42.5)
            self.assertEqual(session_data['prediction']['stage'], 'Pre-Cancerous Stage I')


if __name__ == '__main__':
    unittest.main()