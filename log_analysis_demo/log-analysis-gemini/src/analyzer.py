import json
import csv
import os
from collections import deque

class LogAnalyzer:
    def __init__(self):
        # Updated error patterns to match log level formats and avoid false positives
        self.error_patterns = [
            "[error]", "[exception]", "[fail]", "[fatal]", "[critical]",
            " error ", " exception ", " fail ", " fatal ", " critical "
        ]
        # Non-error log levels to exclude
        self.non_error_levels = ["[warning]", "[info]", "[debug]", "[notice]"]

    def analyze_large_log_file(self, log_file_path, context_lines=3, output_format="json"):
        """
        Analyze large log files efficiently without loading entire file into memory.
        Detects errors and extracts context around them.
        """
        if not os.path.exists(log_file_path):
            return {"error": f"Log file not found: {log_file_path}"}

        errors_with_context = []
        all_lines = []  # Store all lines for context extraction

        try:

            #Instead of the two passes, i can use queue to store only context_lines before the error for optimization(not reading the file 2 times)

            # First pass: read all lines
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_number, line in enumerate(file, 1):
                    line = line.rstrip('\n\r')
                    all_lines.append({
                        'line_number': line_number,
                        'content': line
                    })

            # Second pass: find errors and extract context
            for i, line_data in enumerate(all_lines):
                if self._is_error_line(line_data['content']):
                    error_data = self._extract_error_with_context_from_lines(all_lines, i, context_lines)
                    if error_data:
                        errors_with_context.append(error_data)

            # Save results in requested format
            output_data = {
                "total_errors_found": len(errors_with_context),
                "log_file": log_file_path,
                "errors": errors_with_context
            }

            # Save to file and return both data and save results
            save_result = self._save_results(output_data, output_format)
            
            # Return combined result with both data and save info
            return {
                "data": output_data,
                "save_result": save_result,
                "total_errors": len(errors_with_context),
                "output_file": save_result.get("output_file") if save_result.get("success") else None
            }

        except Exception as e:
            return {"error": f"Error processing log file: {str(e)}"}

    def _is_error_line(self, line):
        """Check if a line contains error log levels (not just the word 'error' in messages)."""
        line_lower = line.lower()
        # Check if line contains error log level AND doesn't contain warning/info/debug levels
        has_error_level = any(pattern in line_lower for pattern in self.error_patterns)
        has_non_error_level = any(level in line_lower for level in self.non_error_levels)

        return has_error_level and not has_non_error_level

    def _extract_error_with_context_from_lines(self, all_lines, error_index, context_lines):
        """Extract error line with surrounding context from the full lines list."""
        if error_index < 0 or error_index >= len(all_lines):
            return None

        error_line = all_lines[error_index]

        # Get context lines before and after
        start_before = max(0, error_index - context_lines)
        end_after = min(len(all_lines), error_index + context_lines + 1)

        context_before = []
        context_after = []

        # Extract context before
        for i in range(start_before, error_index):
            context_before.append({
                'line_number': all_lines[i]['line_number'],
                'content': all_lines[i]['content']
            })

        # Extract context after
        for i in range(error_index + 1, end_after):
            context_after.append({
                'line_number': all_lines[i]['line_number'],
                'content': all_lines[i]['content']
            })

        return {
            "error_line": error_line['content'],
            "line_number": error_line['line_number'],
            "context_before": context_before,
            "context_after": context_after,
            "timestamp": self._extract_timestamp(error_line['content'])
        }

    def _extract_timestamp(self, line):
        """Extract timestamp from log line if present."""
        import re
        # Common timestamp patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',  # MM/DD/YYYY HH:MM:SS
            r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',  # YYYY/MM/DD HH:MM:SS
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()
        return None

    def _save_results(self, data, output_format, output_dir=None):
        """Save analysis results in JSON or CSV format."""
        if output_dir is None:
            # Default to the main project output directory
            output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if output_format.lower() == "json":
            output_file = os.path.join(output_dir, "error_analysis.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif output_format.lower() == "csv":
            output_file = os.path.join(output_dir, "error_analysis.csv")
            self._save_as_csv(data, output_file)
        else:
            return {"error": f"Unsupported output format: {output_format}"}

        return {
            "success": True,
            "output_file": output_file,
            "total_errors": data["total_errors_found"],
            "format": output_format
        }

    def _save_as_csv(self, data, output_file):
        """Save error analysis results as CSV."""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['line_number', 'error_line', 'timestamp', 'context_before', 'context_after']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for error in data["errors"]:
                writer.writerow({
                    'line_number': error['line_number'],
                    'error_line': error['error_line'],
                    'timestamp': error.get('timestamp', ''),
                    'context_before': '; '.join([f"[{item['line_number']}] {item['content']}" for item in error['context_before']]),
                    'context_after': '; '.join([f"[{item['line_number']}] {item['content']}" for item in error['context_after']])
                })

    def prepare_for_llm_from_memory(self, analysis_data):
        """
        Prepare structured error data for LLM API consumption using in-memory data.
        More efficient than loading from saved JSON file.
        Returns formatted text that can be sent to Gemini/OpenAI.
        """
        if not analysis_data or "error" in analysis_data:
            return f"Error in analysis data: {analysis_data.get('error', 'Unknown error')}"

        total_errors = analysis_data.get('total_errors_found', 0)
        errors = analysis_data.get('errors', [])
        log_file = analysis_data.get('log_file', 'unknown')

        formatted_text = f"Log Analysis Summary:\n"
        formatted_text += f"Total errors found: {total_errors}\n"
        formatted_text += f"Log file: {log_file}\n\n"

        for i, error in enumerate(errors, 1):
            formatted_text += f"Error #{i} (Line {error['line_number']}):\n"
            formatted_text += f"Error: {error['error_line']}\n"

            if error.get('context_before'):
                formatted_text += "Context Before:\n"
                for ctx in error['context_before']:
                    formatted_text += f"  [{ctx['line_number']}] {ctx['content']}\n"

            if error.get('context_after'):
                formatted_text += "Context After:\n"
                for ctx in error['context_after']:
                    formatted_text += f"  [{ctx['line_number']}] {ctx['content']}\n"

            formatted_text += "\n" + "="*50 + "\n"

        return formatted_text