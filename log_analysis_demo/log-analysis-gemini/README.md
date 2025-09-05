# Advanced Log Analysis with Gemini AI

This project provides an efficient log analysis system that can handle large log files (thousands of lines) without loading everything into memory. It detects errors, extracts context, and prepares data for LLM analysis.

## 🚀 Features

- **Memory Efficient**: Processes large log files line by line
- **Error Detection**: Identifies errors using multiple patterns (ERROR, Exception, FAIL, etc.)
- **Context Extraction**: Captures N lines before and after each error
- **Structured Output**: Saves results in JSON or CSV format
- **LLM Ready**: Formats data for Gemini/OpenAI API consumption
- **Scalable**: Handles files with thousands of lines efficiently

## 📁 Project Structure

```
log-analysis-gemini/
├── src/
│   ├── start.py              # Application entry point
│   ├── main.py               # Main analysis workflow
│   ├── analyzer.py           # Advanced LogAnalyzer class
│   ├── config.py             # Configuration management
│   └── api/
│       └── gemini_client.py  # Gemini API integration
├── logs/                   # Log files directory
│   └── *.txt               # Your log files (auto-detected)
├── output/                   # Analysis results
├── tests/                    # Unit tests
│   ├── test_analyzer.py      # Tests for LogAnalyzer
│   └── test_gemini_client.py # Tests for GeminiClient
├── pyproject.toml            # Project configuration
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🛠️ Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Gemini API key:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## � Advanced Features

### Interactive File Selection
When multiple log files are present, the system offers interactive selection:
```
Found 2 log files:
1. simulator_test.txt (102.8 KB)
2. test_log.txt (102.8 KB)

Auto-selected most recent: simulator_test.txt

Press Enter to use auto-selected file, or enter file number:
```

### Analysis Summary
Get instant insights with the built-in summary:
```
📊 Analysis Summary:
   • Total errors: 8
   • Error breakdown:
     - ERROR: 8
   • Error lines: 104 - 1294
```

## 📋 Output Files

After analysis, you'll find these files in the `output/` directory:

- **`error_analysis.json`**: Structured error data with context
- **`llm_input.txt`**: Formatted data ready for LLM APIs
- **`gemini_analysis.txt`**: AI-generated insights (if API key provided)
- **`error_analysis.csv`**: CSV format of error analysis

## 🔍 Error Detection Patterns

The system detects errors using these patterns:
- ERROR, Exception, FAIL, FATAL, CRITICAL
- error, exception, fail, fatal, critical

## ⚡ Performance

- **Memory Usage**: O(1) - constant memory regardless of file size
- **Time Complexity**: O(N) - linear time proportional to file size
- **Context Buffer**: Uses deque for efficient sliding window

## 📈 Sample Output

```
🔍 Analyzing log file for errors...
✅ Found 45 errors
📁 Results saved to: output/error_analysis.json
🤖 LLM-ready data prepared (15432 characters)

📋 Sample Errors Found:
1. Line 3: 2023-09-04 10:10:00 ERROR Database connection failed
2. Line 5: 2023-09-04 10:20:00 ERROR Invalid user input
3. Line 8: 2023-09-04 10:35:00 ERROR Network timeout occurred
```

## 🔧 Configuration

Edit `.env` file to customize:
```bash
GEMINI_API_KEY=your_api_key_here
LOG_FILE_PATH=logs/your_custom_log.log
ANALYSIS_OUTPUT_PATH=output/custom_analysis.json
```

## 🤖 LLM Integration

The system automatically formats error data for LLM consumption. Example prompt structure:
```
Log Analysis Summary:
Total errors found: 45
Log file: /path/to/logfile.log

Error #1 (Line 3):
Error: 2023-09-04 10:10:00 ERROR Database connection failed
Context Before:
  [1] 2023-09-04 10:00:00 INFO User login successful
  [2] 2023-09-04 10:05:00 WARNING High memory usage detected
```

## 📝 License

This project is open source and available under the MIT License.