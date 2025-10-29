import os
import requests
import time
import base64
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
JUDGE0_API_URL = f"https://{os.getenv('JUDGE0_API_HOST', 'judge0-ce.p.rapidapi.com')}"
JUDGE0_API_KEY = os.getenv('JUDGE0_API_KEY')
JUDGE0_API_HOST = os.getenv('JUDGE0_API_HOST', 'judge0-ce.p.rapidapi.com')

# Mapping our language names to Judge0's language IDs
# Complete language support with proper IDs
# Reference: https://api.judge0.com/languages
LANGUAGE_ID_MAP = {
    "python": 71,      # Python 3.8.1
    "java": 62,        # Java (OpenJDK 13.0.1)
    "cpp": 54,         # C++ (GCC 9.2.0)
    "c": 50,           # C (GCC 9.2.0)
    "javascript": 63,  # JavaScript (Node.js 12.14.0)
    "go": 60,          # Go (1.13.5)
    "rust": 73,        # Rust (1.40.0)
    "ruby": 72,        # Ruby (2.7.0)
}

class Judge0ExecutionService:
    def __init__(self):
        self.headers = {
            "X-RapidAPI-Key": JUDGE0_API_KEY,
            "X-RapidAPI-Host": JUDGE0_API_HOST,
            "Content-Type": "application/json"
        }

    def run_tests(self, language: str, code: str, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executes code against multiple test cases and returns the results.
        """
        if not JUDGE0_API_KEY:
            raise ValueError("JUDGE0_API_KEY not configured")
            
        if language not in LANGUAGE_ID_MAP:
            raise ValueError(f"Unsupported language: {language}")

        # Language-specific code preparation for automatic execution
        if language == "python":
            # Python: Auto-execute first function with stdin as JSON
            runner = (
                "\n\nif __name__ == \"__main__\":\n"
                "    import sys, json, inspect\n"
                "    raw = sys.stdin.read().strip()\n"
                "    try:\n"
                "        data = json.loads(raw) if raw else None\n"
                "    except Exception:\n"
                "        data = raw\n"
                "    funcs = [obj for name, obj in globals().items() if inspect.isfunction(obj) and getattr(obj, '__module__', '') == '__main__']\n"
                "    result = None\n"
                "    if funcs:\n"
                "        f = funcs[0]\n"
                "        try:\n"
                "            if data is None:\n"
                "                result = f()\n"
                "            elif isinstance(data, dict):\n"
                "                result = f(**data)\n"
                "            elif isinstance(data, list):\n"
                "                result = f(*data)\n"
                "            else:\n"
                "                result = f(data)\n"
                "        except Exception as e:\n"
                "            sys.stderr.write(f'Runtime Error: {str(e)}\\n')\n"
                "            raise SystemExit(1)\n"
                "    if result is not None:\n"
                "        try:\n"
                "            print(json.dumps(result) if not isinstance(result, str) else result)\n"
                "        except Exception:\n"
                "            print(str(result))\n"
                "    elif not funcs:\n"
                "        sys.stderr.write('No callable function found to execute\\n')\n"
                "        raise SystemExit(1)\n"
            )
            source_to_send = f"{code}{runner}"
        
        elif language == "c":
            # C: Ensure proper includes and main function
            if "int main" not in code and "void main" not in code:
                # Wrap code in main if not present
                c_wrapper = (
                    "#include <stdio.h>\n"
                    "#include <stdlib.h>\n"
                    "#include <string.h>\n"
                    f"{code}\n"
                    "int main() {\n"
                    "    // Auto-wrapped main function\n"
                    "    return 0;\n"
                    "}\n"
                )
                source_to_send = c_wrapper
            else:
                source_to_send = code
        
        elif language == "cpp":
            # C++: Ensure proper includes
            if "#include" not in code:
                cpp_includes = (
                    "#include <iostream>\n"
                    "#include <vector>\n"
                    "#include <string>\n"
                    "#include <algorithm>\n"
                    "using namespace std;\n\n"
                )
                source_to_send = cpp_includes + code
            else:
                source_to_send = code
        
        elif language == "java":
            # Java: Ensure proper class structure
            if "public class" not in code and "class Solution" not in code:
                java_wrapper = (
                    f"public class Main {{\n"
                    f"{code}\n"
                    f"}}\n"
                )
                source_to_send = java_wrapper
            else:
                source_to_send = code
        
        else:
            # Other languages: use as-is
            source_to_send = code

        # Base64 encode the source code and test case inputs/outputs
        # This is a Judge0 requirement and prevents issues with special characters.
        encoded_code = base64.b64encode(source_to_send.encode('utf-8')).decode('utf-8')
        
        submissions = []
        for test_case in test_cases:
            # Ensure inputs/outputs are JSON-serializable strings so the runner can read them accurately
            import json as _json
            stdin = test_case.get("input", "")
            expected_output = test_case.get("output", test_case.get("expected_output", ""))
            try:
                stdin_b64 = base64.b64encode(_json.dumps(stdin).encode('utf-8')).decode('utf-8')
            except Exception:
                stdin_b64 = base64.b64encode(str(stdin).encode('utf-8')).decode('utf-8')
            try:
                expected_b64 = base64.b64encode(_json.dumps(expected_output).encode('utf-8')).decode('utf-8')
            except Exception:
                expected_b64 = base64.b64encode(str(expected_output).encode('utf-8')).decode('utf-8')

            submission_payload = {
                "language_id": LANGUAGE_ID_MAP[language],
                "source_code": encoded_code,
                "stdin": stdin_b64,
                "expected_output": expected_b64,
            }
            submissions.append(submission_payload)

        try:
            # 1. Create a batch submission to Judge0
            response = requests.post(
                f"{JUDGE0_API_URL}/submissions/batch?base64_encoded=true",
                headers=self.headers,
                json={"submissions": submissions},
                timeout=30
            )
            response.raise_for_status()
            
            # Get the submission tokens to poll for results
            tokens = [sub['token'] for sub in response.json()]
            
            # 2. Poll for the results
            # We keep checking the API until all submissions are processed.
            results = []
            retries = 20  # Poll for a maximum of ~20 seconds to reduce 'no result' cases
            while len(tokens) > 0 and retries > 0:
                time.sleep(1) # Wait a second between checks
                
                token_str = ",".join(tokens)
                response = requests.get(
                    f"{JUDGE0_API_URL}/submissions/batch?tokens={token_str}&base64_encoded=true&fields=*",
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                
                processed_submissions = response.json().get('submissions', [])
                
                # Filter out tokens that are still processing
                finished_tokens = {sub['token'] for sub in processed_submissions if sub['status']['id'] > 2}
                
                results.extend(processed_submissions)
                tokens = [t for t in tokens if t not in finished_tokens]
                retries -= 1

            # 3. Format the results into a clean structure for our frontend
            return self._format_results(results, test_cases)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Judge0 API error: {str(e)}")

    def _format_results(self, judge0_results: List[Dict[str, Any]], original_test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted = []
        
        # Normalize and match results to test cases using the same encoding as submission
        import json as _json
        used_indices = set()
        
        for i, test_case in enumerate(original_test_cases):
            # Encode stdin exactly as during submission
            stdin_val = test_case.get("input", "")
            try:
                encoded_stdin = base64.b64encode(_json.dumps(stdin_val).encode('utf-8')).decode('utf-8')
            except Exception:
                encoded_stdin = base64.b64encode(str(stdin_val).encode('utf-8')).decode('utf-8')
            
            # Find matching result by encoded stdin first
            result = None
            for idx, res in enumerate(judge0_results):
                if idx in used_indices:
                    continue
                if res.get('stdin') == encoded_stdin:
                    result = res
                    used_indices.add(idx)
                    break
            # If not found, fall back to the first unused result to avoid 'no result'
            if not result:
                for idx, res in enumerate(judge0_results):
                    if idx not in used_indices:
                        result = res
                        used_indices.add(idx)
                        break
            
            if not result:
                # Create a failed result if no matching result found
                formatted_result = {
                    "passed": False,
                    "input": test_case.get("input"),
                    "expected": test_case.get("output", test_case.get("expected_output")),
                    "output": "",
                    "execution_time": 0,
                    "memory": 0,
                    "error": "No result received from Judge0",
                    "debug_info": {
                        "status": "No result",
                        "raw_output": "",
                        "comparison": "No output to compare"
                    }
                }
                formatted.append(formatted_result)
                continue
            
            status_id = result.get('status', {}).get('id')
            
            # Decode the outputs
            stdout = base64.b64decode(result.get('stdout', '') or b'').decode('utf-8').strip()
            stderr = base64.b64decode(result.get('stderr', '') or b'').decode('utf-8').strip()
            compile_output = base64.b64decode(result.get('compile_output', '') or b'').decode('utf-8').strip()
            expected = test_case.get("output", test_case.get("expected_output"))
            
            # Compare outputs using our own logic
            comparison = self._compare_outputs(stdout, expected)
            
            # Determine pass/fail status based on our comparison, not just Judge0's status
            # Use Judge0 status for compilation/runtime errors (status != 3 and not 4)
            # But use our comparison for actual output matching
            if status_id == 3:
                # Judge0 says Accepted - definitely passed
                passed = True
            elif status_id == 4:
                # Judge0 says Wrong Answer - use our comparison logic
                # Our comparison is more flexible (handles whitespace, etc.)
                passed = comparison.get("match", False)
            else:
                # Compilation error, runtime error, timeout, etc. - definitely failed
                passed = False
            
            # Create detailed debug information
            debug_info = {
                "status": result.get('status', {}).get('description', 'Unknown'),
                "status_id": status_id,
                "raw_output": stdout,
                "raw_error": stderr,
                "compile_output": compile_output,
                "comparison": comparison,
                "execution_details": {
                    "time": result.get('time', '0.0'),
                    "memory": result.get('memory', 0),
                    "wall_time": result.get('wall_time', '0.0'),
                    "exit_code": result.get('exit_code', 0),
                    "exit_signal": result.get('exit_signal', 0)
                }
            }
            
            # Get error message (if any)
            # For wrong answers without compilation/runtime errors, error_message will be None
            # allowing the frontend to display the expected vs actual comparison
            error_message = self._get_error_message(result)

            formatted_result = {
                "passed": passed,
                "input": test_case.get("input"),
                "expected": expected,
                "output": stdout,
                "execution_time": float(result.get('time', '0.0') or '0.0') * 1000, # Convert to ms
                "memory": result.get('memory', 0),
                "error": error_message if error_message else None,
                "debug_info": debug_info
            }
            formatted.append(formatted_result)
            
        return formatted

    def _compare_outputs(self, actual: str, expected: str) -> Dict[str, Any]:
        """Compare actual output with expected output and provide detailed analysis"""
        import json as _json
        
        # Coerce non-string values (e.g., booleans, numbers) to strings before trimming
        actual_clean = str(actual).strip()
        expected_clean = str(expected).strip()
        
        # Exact match
        if actual_clean == expected_clean:
            return {
                "match": True,
                "type": "exact",
                "message": "Output matches exactly"
            }
        
        # Try to parse both as JSON and compare
        try:
            actual_json = _json.loads(actual_clean)
            expected_json = _json.loads(expected_clean)
            if actual_json == expected_json:
                return {
                    "match": True,
                    "type": "json_match",
                    "message": "Output matches (JSON comparison)"
                }
        except Exception:
            # Not valid JSON, continue with string comparison
            pass
        
        # Check for whitespace differences - still consider as match
        if actual_clean.replace('\n', ' ').replace('\t', ' ').replace(' ', '') == expected_clean.replace('\n', ' ').replace('\t', ' ').replace(' ', ''):
            return {
                "match": True,
                "type": "whitespace",
                "message": "Output matches (ignoring whitespace)",
                "actual": actual_clean,
                "expected": expected_clean
            }
        
        # Check for case differences - still consider as match for most cases
        if actual_clean.lower() == expected_clean.lower():
            return {
                "match": True,
                "type": "case",
                "message": "Output matches (case insensitive)",
                "actual": actual_clean,
                "expected": expected_clean
            }
        
        # Check for trailing newline differences - still consider as match
        if actual_clean == expected_clean + '\n' or actual_clean + '\n' == expected_clean:
            return {
                "match": True,
                "type": "newline",
                "message": "Output matches (ignoring trailing newlines)",
                "actual": actual_clean,
                "expected": expected_clean
            }
        
        # Partial match analysis
        actual_lines = actual_clean.split('\n')
        expected_lines = expected_clean.split('\n')
        
        return {
            "match": False,
            "type": "different",
            "message": f"Output differs - Got {len(actual_lines)} lines, expected {len(expected_lines)} lines",
            "actual": actual_clean,
            "expected": expected_clean,
            "line_analysis": {
                "actual_lines": actual_lines,
                "expected_lines": expected_lines,
                "first_difference": self._find_first_difference(actual_lines, expected_lines)
            }
        }
    
    def _find_first_difference(self, actual_lines: List[str], expected_lines: List[str]) -> Dict[str, Any]:
        """Find the first line where actual and expected differ"""
        min_len = min(len(actual_lines), len(expected_lines))
        
        for i in range(min_len):
            if actual_lines[i] != expected_lines[i]:
                return {
                    "line_number": i + 1,
                    "actual_line": actual_lines[i],
                    "expected_line": expected_lines[i]
                }
        
        if len(actual_lines) > len(expected_lines):
            return {
                "line_number": min_len + 1,
                "actual_line": actual_lines[min_len],
                "expected_line": None,
                "message": "Extra line in actual output"
            }
        elif len(expected_lines) > len(actual_lines):
            return {
                "line_number": min_len + 1,
                "actual_line": None,
                "expected_line": expected_lines[min_len],
                "message": "Missing line in actual output"
            }
        
        return {"message": "No differences found"}

    def _get_error_message(self, result: Dict[str, Any]) -> str | None:
        status_id = result.get('status', {}).get('id')
        
        if status_id == 3: # Accepted
            return None
        
        # Decode error messages if they exist
        compile_error = base64.b64decode(result.get('compile_output', '') or b'').decode('utf-8')
        runtime_error = base64.b64decode(result.get('stderr', '') or b'').decode('utf-8')
        
        if compile_error:
            return f"Compilation Error: {compile_error}"
        if runtime_error:
            return f"Runtime Error: {runtime_error}"
        
        # For wrong answer status (4), don't return an error message
        # This allows the frontend to display expected vs actual output comparison
        if status_id == 4:
            return None
        
        # For other errors (timeout, memory limit, etc.), return the status description
        return result.get('status', {}).get('description', 'An unknown error occurred')


# Create a singleton instance to be used across the application
judge0_execution_service = Judge0ExecutionService()
