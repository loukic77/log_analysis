# filepath: log-analysis-gemini/src/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", os.path.join(os.path.dirname(__file__), "..", "logs", "default.log"))
    ANALYSIS_OUTPUT_PATH = os.getenv("ANALYSIS_OUTPUT_PATH", os.path.join(os.path.dirname(__file__), "..", "output", "report.txt"))

def load_config():
    # Simple helper to return config as a dict for other modules to use
    return {
        "GEMINI_API_KEY": Config.GEMINI_API_KEY,
        "LOG_FILE_PATH": Config.LOG_FILE_PATH,
        "ANALYSIS_OUTPUT_PATH": Config.ANALYSIS_OUTPUT_PATH,
    }