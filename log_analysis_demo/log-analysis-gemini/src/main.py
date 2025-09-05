import os
from config import load_config
from analyzer import LogAnalyzer
from api.gemini_client import GeminiClient

def find_available_log_files(logs_dir):
    """Find all .txt files in the logs directory."""
    if not os.path.exists(logs_dir):
        return []
    
    txt_files = []
    for file in os.listdir(logs_dir):
        if file.endswith('.txt'):
            txt_files.append(os.path.join(logs_dir, file))
    
    return sorted(txt_files, key=os.path.getmtime, reverse=True)  # Most recent first

def select_log_file(logs_dir):
    """Find and select a log file to analyze."""
    available_files = find_available_log_files(logs_dir)

    if not available_files:
        print(f"No .txt files found in {logs_dir}")
        print("Please place your log file in the logs folder and run again.")
        return None

    if len(available_files) == 1:
        selected_file = available_files[0]
        print(f"Found 1 log file: {os.path.basename(selected_file)}")
    else:
        print(f"Found {len(available_files)} log files:")
        for i, file_path in enumerate(available_files, 1):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # Size in KB
            print(f"{i}. {file_name} ({file_size:.1f} KB)")

        # Auto-select the most recent file
        selected_file = available_files[0]
        print(f"\nAuto-selected most recent: {os.path.basename(selected_file)}")

        # Optional: Allow manual selection
        try:
            choice = input("\nPress Enter to use auto-selected file, or enter file number: ").strip()
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(available_files):
                    selected_file = available_files[idx]
                    print(f"Selected: {os.path.basename(selected_file)}")
        except (ValueError, EOFError):
            pass  # Use auto-selected file

    return selected_file

def print_analysis_summary(analysis_data):
    """Print a summary of the analysis results."""
    if not analysis_data or "error" in analysis_data:
        return

    total_errors = analysis_data.get('total_errors_found', 0)
    errors = analysis_data.get('errors', [])

    if total_errors == 0:
        print("✅ No errors found in the log file.")
        return

    print(f"\n📊 Analysis Summary:")
    print(f"   • Total errors: {total_errors}")

    # Count error types
    error_types = {}
    for error in errors:
        error_line = error.get('error_line', '')
        # Extract log level from error line
        if '[' in error_line and ']' in error_line:
            level = error_line.split('[')[1].split(']')[0]
            error_types[level] = error_types.get(level, 0) + 1

    if error_types:
        print("   • Error breakdown:")
        for level, count in error_types.items():
            print(f"     - {level}: {count}")

    # Show line number range
    if errors:
        line_numbers = [e.get('line_number', 0) for e in errors]
        print(f"   • Error lines: {min(line_numbers)} - {max(line_numbers)}")

def run_analysis(config):
    # Create the Gemini client with the API key
    gemini_client = GeminiClient(api_key=config.get("GEMINI_API_KEY"))
    
    # Create the log analyzer
    log_analyzer = LogAnalyzer()
    
    # Find and select log file from logs directory
    logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    log_file_path = select_log_file(logs_dir)
    
    if not log_file_path:
        return
    
    print(f"Analyzing log file: {log_file_path}")
    
    # Perform detailed error analysis with context
    analysis_results = log_analyzer.analyze_large_log_file(
        log_file_path=log_file_path,
        context_lines=5,  # Extract 5 lines before/after each error
        output_format="json"  # Save as JSON
    )
    
    if "error" in analysis_results:
        print(f"Analysis error: {analysis_results['error']}")
        return
    
    print(f"Found {analysis_results['total_errors']} errors with context")
    print(f"Results saved to: {analysis_results['output_file']}")

    # Print summary
    print_analysis_summary(analysis_results['data'])

    # Prepare data for LLM API - use in-memory data directly
    llm_formatted_data = log_analyzer.prepare_for_llm_from_memory(analysis_results['data'])
    
    # Save LLM-ready data
    output_dir = os.path.dirname(config.get("ANALYSIS_OUTPUT_PATH"))
    llm_output_path = os.path.join(output_dir, "llm_input.txt")
    with open(llm_output_path, 'w', encoding='utf-8') as f:
        f.write(llm_formatted_data)
    
    print(f"LLM-ready data saved to: {llm_output_path}")
    
    # Optional: Send to Gemini for further analysis
    if config.get("GEMINI_API_KEY") and analysis_results['total_errors'] > 0:
        print("\nSending error analysis to Gemini for insights...")
        
        # Use the formatted error data from the analyzer instead of raw log file
        prompt = f"""You are an expert 5G Core Network engineer. You will analyze the following error data extracted from 5G network logs.

Follow these rules strictly:

1. Analyze each ERROR provided in the data below.
2. For each ERROR:
   - Print the error number and line information.
   - Provide a concise explanation of what the error means.
   - Use the context provided (lines before/after) to infer the possible root cause.
3. Suggest practical next steps or troubleshooting actions an engineer should take.
4. Output format must be structured like this:

[ERROR #1]
Line: <line number>
Message: <exact error log>
Explanation: <short explanation>
Context Analysis: <reasoning from nearby logs>
Suggested Fix: <practical step>

[ERROR #2]
...

At the end, provide a short summary of recurring issues or patterns.

ERROR DATA:
{llm_formatted_data}

"""
        
        gemini_response = gemini_client.fetch_data(prompt)
        
        if gemini_response:
            gemini_output_path = os.path.join(output_dir, "gemini_analysis.txt")
            with open(gemini_output_path, 'w', encoding='utf-8') as f:
                f.write("Gemini AI Analysis:\n" + "="*50 + "\n\n")
                f.write("\n".join(gemini_response))
            print(f"Gemini analysis saved to: {gemini_output_path}")
        else:
            print("Failed to get response from Gemini API")
    
    print("Analysis complete!")