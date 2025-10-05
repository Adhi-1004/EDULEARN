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
# You can find more here: https://api.judge0.com/languages
LANGUAGE_ID_MAP = {
    "python": 71,
    "javascript": 63,
    "java": 62,
    "cpp": 54,
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

        # Base64 encode the source code and test case inputs/outputs
        # This is a Judge0 requirement and prevents issues with special characters.
        encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')
        
        submissions = []
        for test_case in test_cases:
            stdin = test_case.get("input", "")
            expected_output = test_case.get("output", test_case.get("expected_output", ""))

            submission_payload = {
                "language_id": LANGUAGE_ID_MAP[language],
                "source_code": encoded_code,
                "stdin": base64.b64encode(str(stdin).encode('utf-8')).decode('utf-8'),
                "expected_output": base64.b64encode(str(expected_output).encode('utf-8')).decode('utf-8'),
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
            retries = 10  # Poll for a maximum of 10 seconds
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
        
        # Create a dictionary for quick lookup by token
        results_map = {res['token']: res for res in judge0_results}
        
        for i, test_case in enumerate(original_test_cases):
            # Find the corresponding result
            result = None
            for token, res in results_map.items():
                if res.get('stdin') == base64.b64encode(str(test_case.get("input", "")).encode('utf-8')).decode('utf-8'):
                    result = res
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
                    "error": "No result received from Judge0"
                }
                formatted.append(formatted_result)
                continue
            
            status_id = result.get('status', {}).get('id')
            
            # Decode the outputs
            stdout = base64.b64decode(result.get('stdout', '') or b'').decode('utf-8').strip()
            expected = test_case.get("output", test_case.get("expected_output"))
            
            # Determine pass/fail status
            passed = (status_id == 3) # Status 3 is "Accepted"
            
            formatted_result = {
                "passed": passed,
                "input": test_case.get("input"),
                "expected": expected,
                "output": stdout,
                "execution_time": float(result.get('time', '0.0') or '0.0') * 1000, # Convert to ms
                "memory": result.get('memory', 0),
                "error": self._get_error_message(result)
            }
            formatted.append(formatted_result)
            
        return formatted

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
        
        return result.get('status', {}).get('description', 'An unknown error occurred')


# Create a singleton instance to be used across the application
judge0_execution_service = Judge0ExecutionService()
