import unittest
from src.api.gemini_client import GeminiClient

class TestGeminiClient(unittest.TestCase):

    def setUp(self):
        self.client = GeminiClient(api_key='your_api_key_here')

    def test_fetch_data(self):
        response = self.client.fetch_data()
        self.assertIsNotNone(response)
        self.assertIn('data', response)

    def test_process_response(self):
        sample_response = {
            'data': [
                {'timestamp': '2023-01-01T00:00:00Z', 'level': 'INFO', 'message': 'Test log entry'}
            ]
        }
        processed_data = self.client.process_response(sample_response)
        self.assertEqual(len(processed_data), 1)
        self.assertEqual(processed_data[0]['level'], 'INFO')

if __name__ == '__main__':
    unittest.main()