# filepath: log-analysis-gemini/src/main.py

import os
from config import load_config
from analyzer import LogAnalyzer
from api.gemini_client import GeminiClient

def main():
    config = load_config()
    gemini_client = GeminiClient(api_key=config['GEMINI_API_KEY'])
    
    log_analyzer = LogAnalyzer()
    
    # Fetch log data from the Gemini API
    log_data = gemini_client.fetch_data()
    
    # Analyze the fetched log data
    analysis_results = log_analyzer.analyze_logs(log_data)
    
    # Generate a report based on the analysis
    log_analyzer.generate_report(analysis_results)

def run_analysis(config):
    # Create the Gemini client with the API key
    gemini_client = GeminiClient(api_key=config.get("GEMINI_API_KEY"))
    
    # Create the log analyzer
    log_analyzer = LogAnalyzer()
    
    # Fetch log data from Gemini API (using a sample prompt for log analysis)
    prompt = "Analyze the following log data for errors and patterns."  # You can customize this
    log_data = gemini_client.fetch_data(prompt, log_file_path=config.get("LOG_FILE_PATH"))
    
    # Analyze the logs
    analysis_results = log_analyzer.analyze_logs(log_data)
    
    # Generate and save the report
    log_analyzer.generate_report(analysis_results, output_path=config.get("ANALYSIS_OUTPUT_PATH"))
    
    print("Analysis complete! Check the output file.")

if __name__ == "__main__":
    main()