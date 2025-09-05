import google.generativeai as genai
import os

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        if self.api_key:
            # Configure the real Gemini API
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.use_real_api = True
        else:
            # Fallback to mock if no API key
            self.use_real_api = False
            print("Warning: No API key provided, using mock responses")

    def fetch_data(self, prompt, log_file_path=None):
        if self.use_real_api:
            return self._fetch_real_data(prompt)
        else:
            return self._fetch_mock_data(prompt, log_file_path)

    def _fetch_real_data(self, prompt):
        """Fetch data from real Gemini API"""
        try:
            print(f"Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            print("✅ Received response from Gemini API")
            return self.process_response(response)
        except Exception as e:
            print(f"❌ Error calling Gemini API: {e}")
            # Fallback to mock if API fails
            print("Falling back to mock response...")
            return self._fetch_mock_data(prompt)

    def _fetch_mock_data(self, prompt, log_file_path=None):
        """Mock response for testing/fallback"""
        print(f"🔄 Using mock response (prompt: {prompt[:50]}...)")

        # Read log data from file if provided
        if log_file_path and os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                log_content = f.read()
        else:
            # Fallback to default mock data
            log_content = """2023-09-04 10:00:00 INFO User login successful
2023-09-04 10:05:00 WARNING High memory usage detected
2023-09-04 10:10:00 ERROR Database connection failed
2023-09-04 10:15:00 INFO Backup completed successfully
2023-09-04 10:20:00 ERROR Invalid user input
2023-09-04 10:25:00 WARNING Disk space low
2023-09-04 10:30:00 INFO System restart initiated"""

        # Create a mock response object
        class MockResponse:
            def __init__(self, text):
                self.text = text

        mock_response = MockResponse(log_content)
        return self.process_response(mock_response)

    def process_response(self, response):
        """Process the API response"""
        if response and hasattr(response, 'text') and response.text:
            log_lines = response.text.strip().split('\n')
            return log_lines
        return []