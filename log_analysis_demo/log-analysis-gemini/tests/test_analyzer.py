import unittest
import os
import sys
import tempfile

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzer import LogAnalyzer

class TestLogAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = LogAnalyzer()

    def test_is_error_line(self):
        # Test error pattern detection - only flags actual error log levels
        self.assertTrue(self.analyzer._is_error_line("2023-10-01 [ERROR] Database connection failed"))
        self.assertTrue(self.analyzer._is_error_line("2023-10-01 ERROR Network timeout occurred"))
        self.assertTrue(self.analyzer._is_error_line("2023-10-01 [CRITICAL] System crash"))
        # WARNING lines with 'error' in message should NOT be flagged
        self.assertFalse(self.analyzer._is_error_line("2023-10-01 [WARNING] High error rate detected"))
        self.assertFalse(self.analyzer._is_error_line("2023-10-01 [INFO] Normal operation"))
        self.assertFalse(self.analyzer._is_error_line("2023-10-01 [DEBUG] Debug message"))

    def test_extract_timestamp(self):
        # Test timestamp extraction
        line = "2023-10-01 12:30:45 ERROR Something happened"
        timestamp = self.analyzer._extract_timestamp(line)
        self.assertEqual(timestamp, "2023-10-01 12:30:45")

        line_no_timestamp = "ERROR Something happened without timestamp"
        timestamp = self.analyzer._extract_timestamp(line_no_timestamp)
        self.assertIsNone(timestamp)

    def test_analyze_large_log_file(self):
        # Create a temporary log file for testing
        log_content = """2023-10-01 12:00:00 INFO System started
2023-10-01 12:01:00 ERROR Database connection failed
2023-10-01 12:02:00 INFO System recovered
2023-10-01 12:03:00 ERROR Network timeout occurred
2023-10-01 12:04:00 INFO Process completed"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_file:
            temp_file.write(log_content)
            temp_file_path = temp_file.name

        try:
            result = self.analyzer.analyze_large_log_file(temp_file_path, context_lines=2)

            # Check that we get the expected structure
            self.assertIn('data', result)
            self.assertIn('save_result', result)
            self.assertEqual(result['total_errors'], 2)

            # Check the data structure
            data = result['data']
            self.assertEqual(data['total_errors_found'], 2)
            self.assertEqual(len(data['errors']), 2)

            # Check first error
            first_error = data['errors'][0]
            self.assertEqual(first_error['line_number'], 2)
            self.assertIn('context_before', first_error)
            self.assertIn('context_after', first_error)

        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_prepare_for_llm_from_memory(self):
        # Test LLM data preparation
        test_data = {
            'total_errors_found': 2,
            'log_file': 'test.log',
            'errors': [
                {
                    'line_number': 10,
                    'error_line': 'ERROR Test error',
                    'context_before': [{'line_number': 9, 'content': 'INFO Previous line'}],
                    'context_after': [{'line_number': 11, 'content': 'INFO Next line'}]
                }
            ]
        }

        result = self.analyzer.prepare_for_llm_from_memory(test_data)

        # Check that the result contains expected content
        self.assertIn('Log Analysis Summary', result)
        self.assertIn('Total errors found: 2', result)
        self.assertIn('Error #1 (Line 10)', result)
        self.assertIn('Context Before:', result)
        self.assertIn('Context After:', result)

if __name__ == '__main__':
    unittest.main()