# filepath: log-analysis-gemini/tests/test_analyzer.py

import unittest
from src.analyzer import LogAnalyzer

class TestLogAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = LogAnalyzer()

    def test_analyze_logs(self):
        # Example log data
        log_data = [
            "2023-10-01 12:00:00 INFO Log entry one",
            "2023-10-01 12:01:00 ERROR Log entry two",
            "2023-10-01 12:02:00 WARNING Log entry three"
        ]
        result = self.analyzer.analyze_logs(log_data)
        expected_result = {
            "INFO": 1,
            "ERROR": 1,
            "WARNING": 1
        }
        self.assertEqual(result, expected_result)

    def test_generate_report(self):
        log_data = [
            "2023-10-01 12:00:00 INFO Log entry one",
            "2023-10-01 12:01:00 ERROR Log entry two"
        ]
        self.analyzer.analyze_logs(log_data)
        report = self.analyzer.generate_report()
        self.assertIn("INFO: 1", report)
        self.assertIn("ERROR: 1", report)

if __name__ == '__main__':
    unittest.main()