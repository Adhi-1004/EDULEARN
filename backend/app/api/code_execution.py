from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime

from ..services.code_execution_service import code_execution_service
from ..services.judge0_execution_service import judge0_execution_service
from ..db import get_db
from .endpoints.auth import get_current_user_id

router = APIRouter()

class CodeExecutionRequest(BaseModel):
    code: str = Field(..., min_length=1, description="The code to execute")
    language: str = Field(..., description="Programming language")
    test_cases: Optional[List[Dict[str, Any]]] = Field(default=[], description="Test cases to run")
    timeout: int = Field(default=10, ge=1, le=30, description="Execution timeout in seconds")
    input_data: Optional[str] = Field(default="", description="Input data for the code")
    use_judge0: bool = Field(default=False, description="Use Judge0 API for execution")

class CodeExecutionResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    memory_used: float
    results: Optional[List[Dict[str, Any]]] = None
    passed_tests: Optional[int] = None
    total_tests: Optional[int] = None
    success_rate: Optional[float] = None

class DebugRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: str = Field(...)
    breakpoints: Optional[List[int]] = Field(default=[], description="Line numbers for breakpoints")
    input_data: Optional[str] = Field(default="")

class DebugResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    call_stack: Optional[List[Dict[str, Any]]] = None
    execution_time: float

class TestCaseRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: str = Field(...)
    test_cases: List[Dict[str, Any]] = Field(..., min_items=1)
    timeout: int = Field(default=10, ge=1, le=30)

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Execute code with optional test cases
    """
    try:
        # Choose execution service based on request
        if request.use_judge0:
            # Use Judge0 API for execution
            try:
                if request.test_cases:
                    results = judge0_execution_service.run_tests(
                        language=request.language,
                        code=request.code,
                        test_cases=request.test_cases
                    )
                    
                    passed_tests = sum(1 for r in results if r['passed'])
                    total_tests = len(results)
                    
                    return CodeExecutionResponse(
                        success=True,
                        results=results,
                        passed_tests=passed_tests,
                        total_tests=total_tests,
                        execution_time=sum(r.get('execution_time', 0) for r in results),
                        memory_used=sum(r.get('memory', 0) for r in results)
                    )
                else:
                    # Single execution without test cases
                    single_test = [{"input": "", "output": ""}]
                    results = judge0_execution_service.run_tests(
                        language=request.language,
                        code=request.code,
                        test_cases=single_test
                    )
                    
                    if results:
                        result = results[0]
                        return CodeExecutionResponse(
                            success=result['passed'],
                            output=result.get('output', ''),
                            error=result.get('error', ''),
                            execution_time=result.get('execution_time', 0),
                            memory_used=result.get('memory', 0)
                        )
                    else:
                        return CodeExecutionResponse(
                            success=False,
                            error="No results from Judge0"
                        )
                        
            except Exception as judge0_error:
                # Fallback to local execution if Judge0 fails
                print(f"Judge0 execution failed: {judge0_error}")
                # Continue to local execution
        else:
            # Use local execution service
            if request.language not in code_execution_service.get_supported_languages():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported language: {request.language}"
                )
        
        # Use Gemini coding service for better execution
        from services.gemini_coding_service import gemini_coding_service
        
        if request.test_cases:
            # Execute with test cases using Gemini service
            execution_result = gemini_coding_service.execute_code(
                code=request.code,
                language=request.language,
                test_cases=request.test_cases,
                time_limit=request.timeout * 1000,  # Convert to milliseconds
                memory_limit=256
            )
            
            # Format results for response
            results = []
            passed_tests = 0
            total_tests = len(execution_result.get('results', []))
            
            for i, test_result in enumerate(execution_result.get('results', [])):
                results.append({
                    'test_case': i + 1,
                    'input': test_result.get('test_input', ''),
                    'expected_output': test_result.get('expected', ''),
                    'actual_output': test_result.get('output', ''),
                    'passed': test_result.get('passed', False),
                    'execution_time': test_result.get('execution_time', 0),
                    'memory_used': test_result.get('memory_used', 0),
                    'error': test_result.get('error', '')
                })
                if test_result.get('passed', False):
                    passed_tests += 1
            
            return CodeExecutionResponse(
                success=execution_result.get('success', False),
                results=results,
                passed_tests=passed_tests,
                total_tests=total_tests,
                execution_time=execution_result.get('execution_time', 0),
                memory_used=execution_result.get('memory_used', 0)
            )
        else:
            # Simple execution without test cases
            result = await code_execution_service.execute_code(
                code=request.code,
                language=request.language,
                timeout=request.timeout
            )
            
            return CodeExecutionResponse(
                success=result['success'],
                output=result.get('output', ''),
                error=result.get('error', ''),
                execution_time=result.get('execution_time', 0),
                memory_used=result.get('memory_used', 0),
                results=result.get('results'),
                passed_tests=result.get('passed_tests'),
                total_tests=result.get('total_tests'),
                success_rate=result.get('success_rate')
            )
        
    except Exception as e:
        print(f"[ERROR] [EXECUTION] Error in execute_code: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@router.post("/debug", response_model=DebugResponse)
async def debug_code(
    request: DebugRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Debug code with breakpoints and variable inspection
    """
    try:
            # Basic pseudo-debugging by injecting prints; for production use a debugger
        
        debug_code = request.code
        
        # Add debug prints for variables (basic implementation)
        if request.language == 'python':
            # Add print statements for variable inspection
            lines = debug_code.split('\n')
            debug_lines = []
            
            for i, line in enumerate(lines):
                debug_lines.append(line)
                # Add debug prints at breakpoints
                if i + 1 in request.breakpoints:
                    debug_lines.append(f"    print(f'DEBUG: Line {i+1} - Variables: {{locals()}}')")
        
        # Execute with debug information
        result = await code_execution_service.execute_code(
            code='\n'.join(debug_lines),
            language=request.language,
            timeout=10
        )
        
        return DebugResponse(
            success=result['success'],
            output=result.get('output', ''),
            error=result.get('error', ''),
            variables={},  # Would be populated by actual debugger
            call_stack=[],  # Would be populated by actual debugger
            execution_time=result.get('execution_time', 0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test", response_model=CodeExecutionResponse)
async def test_code(
    request: TestCaseRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Run code against test cases
    """
    try:
        result = await code_execution_service.execute_code(
            code=request.code,
            language=request.language,
            test_cases=request.test_cases,
            timeout=request.timeout
        )
        
        return CodeExecutionResponse(
            success=result['success'],
            output=result.get('output', ''),
            error=result.get('error', ''),
            execution_time=result.get('execution_time', 0),
            memory_used=result.get('memory_used', 0),
            results=result.get('results'),
            passed_tests=result.get('passed_tests'),
            total_tests=result.get('total_tests'),
            success_rate=result.get('success_rate')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported programming languages
    """
    languages = code_execution_service.get_supported_languages()
    language_info = {}
    
    for lang in languages:
        info = code_execution_service.get_language_info(lang)
        language_info[lang] = {
            'name': lang.title(),
            'extension': info.get('extension', ''),
            'timeout': info.get('timeout', 10),
            'memory_limit': info.get('memory_limit', 128)
        }
    
    return {
        'languages': languages,
        'language_info': language_info
    }

@router.post("/validate-syntax")
async def validate_syntax(
    request: CodeExecutionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Validate code syntax without execution
    """
    try:
        # For syntax validation, we'll do a quick compilation check
        if request.language == 'python':
            import ast
            try:
                ast.parse(request.code)
                return {'valid': True, 'errors': []}
            except SyntaxError as e:
                return {
                    'valid': False, 
                    'errors': [{'line': e.lineno, 'message': str(e)}]
                }
        
        elif request.language == 'javascript':
            # Basic JS syntax check (would need a proper JS parser in production)
            return {'valid': True, 'errors': []}
        
        elif request.language == 'java':
            # Try to compile without running by executing with no test cases
            result = await code_execution_service.execute_code(
                code=request.code,
                language=request.language,
                timeout=5
            )
            return {
                'valid': result.get('success', False) or not result.get('error'),
                'errors': [result.get('error')] if result.get('error') else []
            }
        
        else:
            return {'valid': True, 'errors': []}
            
    except Exception as e:
        return {'valid': False, 'errors': [str(e)]}

@router.post("/format-code")
async def format_code(
    request: CodeExecutionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Format code according to language standards
    """
    try:
        formatted_code = request.code
        
        if request.language == 'python':
            # Basic Python formatting (would use black/autopep8 in production)
            lines = request.code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped:
                    if stripped.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except:', 'finally:', 'with ')):
                        formatted_lines.append('    ' * indent_level + stripped)
                        if stripped.endswith(':'):
                            indent_level += 1
                    elif stripped.startswith(('return', 'break', 'continue', 'pass')):
                        formatted_lines.append('    ' * indent_level + stripped)
                    else:
                        formatted_lines.append('    ' * indent_level + stripped)
                else:
                    formatted_lines.append('')
            
            formatted_code = '\n'.join(formatted_lines)
        
        return {
            'formatted_code': formatted_code,
            'language': request.language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check for code execution service
    """
    return {
        'status': 'healthy',
        'supported_languages': code_execution_service.get_supported_languages(),
        'timestamp': datetime.utcnow().isoformat()
    }
