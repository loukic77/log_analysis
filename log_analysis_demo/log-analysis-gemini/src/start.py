# filepath: log-analysis-gemini/src/start.py

import os
from config import load_config
from main import run_analysis

def main():
    # Load configuration settings
    config = load_config()
    
    # Initialize the log analysis process
    run_analysis(config)

if __name__ == "__main__":
    main()