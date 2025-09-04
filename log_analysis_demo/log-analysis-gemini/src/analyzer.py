class LogAnalyzer:
    def __init__(self):
        pass

    def analyze_logs(self, log_data):
        # Simple analysis: count errors, warnings, etc.
        if not log_data:
            return {"error": "No log data provided"}
        
        analysis = {
            "total_lines": len(log_data),
            "errors": 0,
            "warnings": 0,
            "info": 0,
            "other": 0
        }
        
        for line in log_data:
            line_lower = line.lower()
            if "error" in line_lower:
                analysis["errors"] += 1
            elif "warning" in line_lower:
                analysis["warnings"] += 1
            elif "info" in line_lower:
                analysis["info"] += 1
            else:
                analysis["other"] += 1
        
        return analysis

    def generate_report(self, analysis_results, output_path="output/report.txt"):
        # Generate a simple text report
        report = f"Log Analysis Report\n{'='*20}\n"
        report += f"Total Lines: {analysis_results.get('total_lines', 0)}\n"
        report += f"Errors: {analysis_results.get('errors', 0)}\n"
        report += f"Warnings: {analysis_results.get('warnings', 0)}\n"
        report += f"Info: {analysis_results.get('info', 0)}\n"
        report += f"Other: {analysis_results.get('other', 0)}\n"
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"Report saved to {output_path}")