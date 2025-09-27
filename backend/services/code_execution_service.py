import subprocess
import tempfile
import os
import time
import psutil
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import signal
import threading
from pathlib import Path

class CodeExecutionService:
    def __init__(self):
        self.supported_languages = {
            'python': {
                'extension': '.py',
                'command': 'python',
                'timeout': 10,
                'memory_limit': 128  # MB
            },
            'javascript': {
                'extension': '.js',
                'command': 'node',
                'timeout': 10,
                'memory_limit': 128
            },
            'java': {
                'extension': '.java',
                'command': 'javac',
                'run_command': 'java',
                'timeout': 15,
                'memory_limit': 256
            },
            'cpp': {
                'extension': '.cpp',
                'command': 'g++',
                'run_command': './a.out',
                'timeout': 15,
                'memory_limit': 256
            },
            'go': {
                'extension': '.go',
                'command': 'go run',
                'timeout': 10,
                'memory_limit': 128
            }
        }
    
    async def execute_code(
        self, 
        code: str, 
        language: str, 
        test_cases: List[Dict[str, Any]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Execute code with test cases and return results
        """
        if language not in self.supported_languages:
            return {
                'success': False,
                'error': f'Unsupported language: {language}',
                'results': [],
                'execution_time': 0,
                'memory_used': 0
            }
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=self.supported_languages[language]['extension'],
                delete=False
            ) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            # Execute code
            if test_cases:
                return await self._execute_with_test_cases(
                    temp_file_path, language, test_cases, timeout
                )
            else:
                return await self._execute_simple(
                    temp_file_path, language, timeout
                )
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'execution_time': 0,
                'memory_used': 0
            }
        finally:
            # Cleanup
            try:
                os.unlink(temp_file_path)
                if language == 'cpp':
                    exe_name = 'a.exe' if os.name == 'nt' else 'a.out'
                    exe_path = os.path.join(os.path.dirname(temp_file_path), exe_name)
                    if os.path.exists(exe_path):
                        os.unlink(exe_path)
            except Exception:
                pass
    
    async def _execute_with_test_cases(
        self, 
        file_path: str, 
        language: str, 
        test_cases: List[Dict[str, Any]], 
        timeout: int
    ) -> Dict[str, Any]:
        """Execute code with multiple test cases"""
        results = []
        total_time = 0
        max_memory = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                # For function-based code, create a wrapper
                if language == 'python':
                    result = await self._execute_python_with_test_case(
                        file_path, test_case, timeout
                    )
                else:
                    # For other languages, use the original method
                    input_data = test_case.get('input', '')
                    expected_output = test_case.get('output', '')
                    
                    start_time = time.time()
                    result = await self._run_code_with_input(
                        file_path, language, input_data, timeout
                    )
                    execution_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    # Check if output matches expected
                    actual_output = result.get('output', '').strip()
                    expected_output = str(expected_output).strip()
                    
                    result = {
                        'input': input_data,
                        'expected_output': expected_output,
                        'actual_output': actual_output,
                        'passed': actual_output == expected_output,
                        'execution_time': execution_time,
                        'memory_used': result.get('memory_used', 0),
                        'error': result.get('error', '')
                    }
                
                test_result = {
                    'test_case': i + 1,
                    'input': test_case.get('input', ''),
                    'expected_output': test_case.get('output', ''),
                    'actual_output': result.get('actual_output', ''),
                    'passed': result.get('passed', False),
                    'execution_time': result.get('execution_time', 0),
                    'memory_used': result.get('memory_used', 0),
                    'error': result.get('error', '')
                }
                
                results.append(test_result)
                total_time += result.get('execution_time', 0)
                max_memory = max(max_memory, result.get('memory_used', 0))
                
            except Exception as e:
                results.append({
                    'test_case': i + 1,
                    'input': test_case.get('input', ''),
                    'expected_output': test_case.get('output', ''),
                    'actual_output': '',
                    'passed': False,
                    'execution_time': 0,
                    'memory_used': 0,
                    'error': str(e)
                })
        
        # Calculate overall success
        passed_tests = sum(1 for r in results if r['passed'])
        success_rate = (passed_tests / len(results)) * 100 if results else 0
        
        return {
            'success': passed_tests == len(results),
            'results': results,
            'execution_time': total_time,
            'memory_used': max_memory,
            'passed_tests': passed_tests,
            'total_tests': len(results),
            'success_rate': success_rate
        }
    
    async def _execute_python_with_test_case(
        self, 
        file_path: str, 
        test_case: Dict[str, Any], 
        timeout: int
    ) -> Dict[str, Any]:
        """Execute Python code with a test case using function-based approach"""
        try:
            # Read the original code
            with open(file_path, 'r') as f:
                original_code = f.read()
            
            # Create a wrapper that handles the test case
            wrapper_code = f"""
import sys
import json
import traceback

try:
    # User's code
    exec('''{original_code}''')
    
    # Test case input
    test_input = {json.dumps(test_case.get('input', {}))}
    expected_output = {json.dumps(test_case.get('output'))}
    
    # Try to find and call the solution function
    if 'solution' in globals():
        result = solution(test_input)
    else:
        # Try to find the first function defined
        import inspect
        functions = [obj for name, obj in globals().items() if inspect.isfunction(obj)]
        if functions:
            result = functions[0](test_input)
        else:
            result = None
    
    # Compare result
    passed = result == expected_output
    
    print(json.dumps({{
        "passed": passed,
        "output": result,
        "expected": expected_output,
        "error": None
    }}))
    
except Exception as e:
    print(json.dumps({{
        "passed": False,
        "output": None,
        "expected": {json.dumps(test_case.get('output'))},
        "error": str(e)
    }}))
"""
            
            # Write wrapper to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(wrapper_code)
                wrapper_path = f.name
            
            # Execute wrapper
            start_time = time.time()
            result = await self._run_command(
                ['python', wrapper_path], 
                timeout=timeout
            )
            execution_time = (time.time() - start_time) * 1000
            
            # Clean up wrapper file
            os.unlink(wrapper_path)
            
            if result['return_code'] == 0:
                # Parse JSON output
                try:
                    output_data = json.loads(result['stdout'])
                    return {
                        'input': test_case.get('input', ''),
                        'expected_output': test_case.get('output', ''),
                        'actual_output': str(output_data.get('output', '')),
                        'passed': output_data.get('passed', False),
                        'execution_time': execution_time,
                        'memory_used': result.get('memory_used', 0),
                        'error': output_data.get('error', '')
                    }
                except json.JSONDecodeError:
                    return {
                        'input': test_case.get('input', ''),
                        'expected_output': test_case.get('output', ''),
                        'actual_output': result['stdout'],
                        'passed': False,
                        'execution_time': execution_time,
                        'memory_used': result.get('memory_used', 0),
                        'error': 'Failed to parse output'
                    }
            else:
                return {
                    'input': test_case.get('input', ''),
                    'expected_output': test_case.get('output', ''),
                    'actual_output': '',
                    'passed': False,
                    'execution_time': execution_time,
                    'memory_used': result.get('memory_used', 0),
                    'error': result['stderr'] or 'Execution failed'
                }
                
        except Exception as e:
            return {
                'input': test_case.get('input', ''),
                'expected_output': test_case.get('output', ''),
                'actual_output': '',
                'passed': False,
                'execution_time': 0,
                'memory_used': 0,
                'error': str(e)
            }
    
    async def _execute_simple(
        self, 
        file_path: str, 
        language: str, 
        timeout: int
    ) -> Dict[str, Any]:
        """Execute code without test cases"""
        try:
            start_time = time.time()
            result = await self._run_code_with_input(
                file_path, language, '', timeout
            )
            execution_time = (time.time() - start_time) * 1000
            
            return {
                'success': not result.get('error'),
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'execution_time': execution_time,
                'memory_used': result.get('memory_used', 0)
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'execution_time': 0,
                'memory_used': 0
            }
    
    async def _run_code_with_input(
        self, 
        file_path: str, 
        language: str, 
        input_data: str, 
        timeout: int
    ) -> Dict[str, Any]:
        """Run code with input and capture output"""
        lang_config = self.supported_languages[language]
        temp_dir = os.path.dirname(file_path)
        
        try:
            if language == 'java':
                # Compile Java first
                compile_result = await self._run_command(
                    [lang_config['command'], file_path], 
                    timeout=timeout,
                    cwd=temp_dir
                )
                if compile_result['return_code'] != 0:
                    return {
                        'output': '',
                        'error': f'Compilation error: {compile_result["stderr"]}',
                        'memory_used': 0
                    }
                
                # Run compiled Java from temp dir classpath
                class_name = os.path.splitext(os.path.basename(file_path))[0]
                run_result = await self._run_command(
                    [lang_config['run_command'], class_name],
                    input_data=input_data,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
            elif language == 'cpp':
                # Compile C++ first
                exe_name = 'a.exe' if os.name == 'nt' else 'a.out'
                exe_path = os.path.join(temp_dir, exe_name)
                compile_result = await self._run_command(
                    [lang_config['command'], '-o', exe_path, file_path],
                    timeout=timeout,
                    cwd=temp_dir
                )
                if compile_result['return_code'] != 0:
                    return {
                        'output': '',
                        'error': f'Compilation error: {compile_result["stderr"]}',
                        'memory_used': 0
                    }
                
                # Run compiled C++
                run_result = await self._run_command(
                    [exe_path],
                    input_data=input_data,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
            elif language == 'go':
                # Go run directly
                run_result = await self._run_command(
                    ['go', 'run', file_path],
                    input_data=input_data,
                    timeout=timeout,
                    cwd=temp_dir
                )
                
            else:
                # Python, JavaScript
                run_result = await self._run_command(
                    [lang_config['command'], file_path],
                    input_data=input_data,
                    timeout=timeout,
                    cwd=temp_dir
                )
            
            return {
                'output': run_result['stdout'],
                'error': run_result['stderr'],
                'memory_used': run_result.get('memory_used', 0)
            }
            
        except Exception as e:
            return {
                'output': '',
                'error': str(e),
                'memory_used': 0
            }
    
    async def _run_command(
        self, 
        command: List[str], 
        input_data: str = '', 
        timeout: int = 10,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run a command with timeout and memory monitoring"""
        process = None
        memory_used = 0
        done_event = threading.Event()
        
        try:
            # Start process
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or os.getcwd()
            )
            
            # Monitor memory usage
            def monitor_memory():
                nonlocal memory_used
                try:
                    while not done_event.is_set():
                        try:
                            proc = psutil.Process(process.pid)
                            if not proc.is_running():
                                break
                            memory_used = max(memory_used, proc.memory_info().rss / 1024 / 1024)  # MB
                        except Exception:
                            pass
                        time.sleep(0.1)
                except Exception:
                    pass
            
            # Start memory monitoring in background
            memory_thread = threading.Thread(target=monitor_memory)
            memory_thread.daemon = True
            memory_thread.start()
            
            # Send input and wait for completion
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=input_data.encode() if input_data else None),
                timeout=timeout
            )
            done_event.set()
            
            return {
                'stdout': stdout.decode('utf-8', errors='ignore'),
                'stderr': stderr.decode('utf-8', errors='ignore'),
                'return_code': process.returncode,
                'memory_used': memory_used
            }
            
        except asyncio.TimeoutError:
            if process:
                process.kill()
            done_event.set()
            return {
                'stdout': '',
                'stderr': f'Execution timed out after {timeout} seconds',
                'return_code': -1,
                'memory_used': memory_used
            }
        except Exception as e:
            if process:
                process.kill()
            done_event.set()
            return {
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'memory_used': memory_used
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        return list(self.supported_languages.keys())
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Get information about a specific language"""
        if language not in self.supported_languages:
            return {}
        return self.supported_languages[language]

# Global instance
code_execution_service = CodeExecutionService()
