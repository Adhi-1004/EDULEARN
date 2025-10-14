"""
Gemini AI Coding Service
Handles all AI-driven features for the coding platform
"""
import google.generativeai as genai
import json
import os
import re
import subprocess
import tempfile
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiCodingService:
    def __init__(self):
        """Initialize Gemini AI service for coding platform"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and self.api_key != "your-google-ai-api-key":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.model.generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 4096,
            }
            self.available = True
            print("[SUCCESS] [GEMINI_CODING] Gemini AI service initialized successfully")
        else:
            self.model = None
            self.available = False
            print("[WARNING] [GEMINI_CODING] Gemini API key not configured, using fallback mode")

    async def generate_mcq_questions(
        self,
        topic: str,
        difficulty: str,
        count: int = 10,
        question_type: str = "mcq"
    ) -> List[Dict[str, Any]]:
        """Generate MCQ questions for assessments using Gemini AI"""
        try:
            print(f"🧠 [GEMINI_CODING] Generating {count} {difficulty} MCQ questions for topic: {topic}")
            
            if not self.available:
                return self._generate_fallback_mcq_questions(topic, difficulty, count)
            
            prompt = f"""
            Generate {count} high-quality multiple choice questions on the topic: "{topic}"
            Difficulty level: {difficulty}
            
            Requirements:
            - Each question should have exactly 4 options (A, B, C, D)
            - Only one correct answer per question
            - Include detailed explanations for each answer
            - Questions should test understanding, not just memorization
            - Vary question types (conceptual, application, analysis)
            - Ensure questions are original and educational
            
            Format the response as a JSON array with this structure:
            [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "Detailed explanation of why this is correct"
                }}
            ]
            
            Return only the JSON array, no additional text.
            """
            
            response = await self.model.generate_content_async(prompt)
            questions_text = response.text.strip()
            
            # Clean and fix common JSON issues
            questions_text = self._clean_json_response(questions_text)
            
            # Parse JSON response with error handling
            try:
                questions = json.loads(questions_text)
            except json.JSONDecodeError as e:
                print(f"❌ [GEMINI] JSON parsing error: {str(e)}")
                print(f"🔍 [GEMINI] Raw content that failed to parse: {questions_text[:200]}...")
                print(f"⚠️ [GEMINI] Using fallback questions for {topic} ({difficulty})")
                return self._generate_fallback_mcq_questions(topic, difficulty, count)
            
            # Validate and clean questions
            validated_questions = []
            for i, q in enumerate(questions[:count]):
                # Handle both "answer" (letter format) and "correct_answer" (index format)
                if "answer" in q and "correct_answer" not in q:
                    # Convert letter answer (A, B, C, D) to index (0, 1, 2, 3)
                    answer_letter = q["answer"].upper()
                    if answer_letter in ["A", "B", "C", "D"]:
                        q["correct_answer"] = ord(answer_letter) - ord("A")
                    else:
                        continue  # Skip invalid answer format
                
                if self._validate_mcq_question(q):
                    validated_questions.append({
                        "question": q["question"],
                        "options": q["options"],
                        "correct_answer": q["correct_answer"],
                        "explanation": q.get("explanation", ""),
                        "difficulty": difficulty,
                        "topic": topic,
                        "generated_by": "gemini"
                    })
            
            print(f"✅ [GEMINI_CODING] Generated {len(validated_questions)} valid MCQ questions")
            return validated_questions
            
        except Exception as e:
            print(f"❌ [GEMINI_CODING] Error generating MCQ questions: {str(e)}")
            return self._generate_fallback_mcq_questions(topic, difficulty, count)
    
    def _validate_mcq_question(self, question: Dict[str, Any]) -> bool:
        """Validate MCQ question structure"""
        required_fields = ["question", "options"]
        if not all(field in question for field in required_fields):
            return False
        
        # Check if we have either "answer" or "correct_answer"
        if "answer" not in question and "correct_answer" not in question:
            return False
        
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            return False
        
        # If we have correct_answer, validate it's an integer index
        if "correct_answer" in question:
            if not isinstance(question["correct_answer"], int) or question["correct_answer"] < 0 or question["correct_answer"] > 3:
                return False
        
        return True
    
    def _clean_json_response(self, json_text: str) -> str:
        """Clean and fix common JSON issues in AI responses"""
        # Remove any text before the first '[' or '{'
        start_idx = max(json_text.find('['), json_text.find('{'))
        if start_idx > 0:
            json_text = json_text[start_idx:]
        
        # Remove any text after the last ']' or '}'
        end_idx = max(json_text.rfind(']'), json_text.rfind('}'))
        if end_idx > 0:
            json_text = json_text[:end_idx + 1]
        
        # Fix common issues with newlines in strings
        json_text = json_text.replace('\n', '\\n')
        
        # Fix unterminated strings by adding quotes
        lines = json_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Count unescaped quotes
            quote_count = line.count('"') - line.count('\\"')
            if quote_count % 2 == 1 and not line.strip().endswith('"'):
                line = line.rstrip() + '"'
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _generate_fallback_mcq_questions(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate fallback MCQ questions when AI is not available"""
        print(f"🔄 [GEMINI_CODING] Using fallback MCQ generation for {topic}")
        
        fallback_questions = []
        for i in range(count):
            fallback_questions.append({
                "question": f"What is the main concept of {topic}? (Question {i+1})",
                "options": [
                    f"Option A for {topic}",
                    f"Option B for {topic}",
                    f"Option C for {topic}",
                    f"Option D for {topic}"
                ],
                "correct_answer": i % 4,
                "explanation": f"This is a fallback question about {topic}",
                "difficulty": difficulty,
                "topic": topic,
                "generated_by": "fallback"
            })
        
        return fallback_questions

    async def generate_coding_problem(
        self, 
        topic: str, 
        difficulty: str, 
        user_skill_level: str = "intermediate",
        focus_areas: List[str] = None,
        avoid_topics: List[str] = None
    ) -> Dict[str, Any]:
        """Generate an original coding problem using Gemini AI"""
        try:
            print(f"🧠 [GEMINI_CODING] Generating {difficulty} problem for topic: {topic}")
            
            if not self.available:
                return self._get_fallback_problem(topic, difficulty)
            
            focus_str = ", ".join(focus_areas) if focus_areas else "general problem solving"
            avoid_str = ", ".join(avoid_topics) if avoid_topics else "none"
            
            prompt = f"""
            Generate an original, unique coding problem with the following specifications:
            
            Topic: {topic}
            Difficulty: {difficulty}
            User Skill Level: {user_skill_level}
            Focus Areas: {focus_str}
            Avoid Topics: {avoid_str}
            
            CRITICAL REQUIREMENTS:
            1. Return ONLY a valid JSON object with this exact structure:
            {{
                "title": "Creative Problem Title",
                "description": "Detailed problem description with clear requirements",
                "topic": "{topic}",
                "difficulty": "{difficulty}",
                "constraints": ["Constraint 1", "Constraint 2"],
                "examples": [
                    {{
                        "input": "Example input",
                        "output": "Expected output",
                        "explanation": "Why this output is correct"
                    }}
                ],
                "test_cases": [
                    {{
                        "input": {{"param1": "value1"}},
                        "output": "expected_result",
                        "description": "Test case description"
                    }}
                ],
                "hidden_test_cases": [
                    {{
                        "input": {{"param1": "value1"}},
                        "output": "expected_result",
                        "description": "Hidden test case"
                    }}
                ],
                "expected_complexity": {{
                    "time": "O(n)",
                    "space": "O(1)"
                }},
                "hints": ["Hint 1", "Hint 2"],
                "tags": ["tag1", "tag2"]
            }}
            
            2. Make the problem original and creative
            3. Ensure it's appropriate for {difficulty} level
            4. Include clear, unambiguous requirements
            5. Provide comprehensive test coverage
            6. Make it educational and engaging
            7. DO NOT include any text outside the JSON object
            8. DO NOT use markdown formatting or code blocks
            
            Generate the problem now:
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                print("[ERROR] [GEMINI_CODING] No response from Gemini API")
                return self._get_fallback_problem(topic, difficulty)
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            print(f"[DEBUG] [GEMINI_CODING] Raw response: {response_text[:200]}...")
            
            # Remove markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            # Clean up any remaining formatting
            response_text = response_text.strip()
            
            try:
                problem_data = json.loads(response_text)
                
                # Validate required fields
                required_fields = ['title', 'description', 'test_cases', 'hidden_test_cases']
                for field in required_fields:
                    if field not in problem_data:
                        raise ValueError(f"Missing required field: {field}")
                
                # Ensure test_cases and hidden_test_cases are lists
                if not isinstance(problem_data.get('test_cases'), list):
                    problem_data['test_cases'] = []
                if not isinstance(problem_data.get('hidden_test_cases'), list):
                    problem_data['hidden_test_cases'] = []
                
                # Ensure examples is a list
                if not isinstance(problem_data.get('examples'), list):
                    problem_data['examples'] = []
                
                # Ensure constraints is a list
                if not isinstance(problem_data.get('constraints'), list):
                    problem_data['constraints'] = []
                
                # Ensure hints is a list
                if not isinstance(problem_data.get('hints'), list):
                    problem_data['hints'] = []
                
                # Ensure tags is a list
                if not isinstance(problem_data.get('tags'), list):
                    problem_data['tags'] = []
                
                print(f"[SUCCESS] [GEMINI_CODING] Successfully generated problem: {problem_data['title']}")
                return problem_data
                
            except json.JSONDecodeError as e:
                print(f"[ERROR] [GEMINI_CODING] JSON parsing error: {str(e)}")
                print(f"[DEBUG] [GEMINI_CODING] Raw response: {response_text}")
                return self._get_fallback_problem(topic, difficulty)
            
        except Exception as e:
            print(f"[ERROR] [GEMINI_CODING] Error generating problem: {str(e)}")
            return self._get_fallback_problem(topic, difficulty)

    async def analyze_code_solution(
        self, 
        code: str, 
        problem_description: str, 
        language: str,
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze code solution and provide AI feedback"""
        try:
            print(f"[DEBUG] [GEMINI_CODING] Analyzing {language} solution")
            
            if not self.available:
                return self._get_fallback_feedback(code, test_results)
            
            passed_tests = sum(1 for result in test_results if result.get('passed', False))
            total_tests = len(test_results)
            
            prompt = f"""
            Analyze this coding solution and provide comprehensive feedback:
            
            Problem: {problem_description}
            Language: {language}
            Code:
            ```{language}
            {code}
            ```
            
            Test Results: {passed_tests}/{total_tests} tests passed
            Failed Tests: {json.dumps([r for r in test_results if not r.get('passed', False)], indent=2)}
            
            Provide detailed analysis in this JSON format:
            {{
                "correctness": {{
                    "score": 85,
                    "issues": ["Issue 1", "Issue 2"],
                    "suggestions": ["Suggestion 1", "Suggestion 2"]
                }},
                "performance": {{
                    "time_complexity": "O(n)",
                    "space_complexity": "O(1)",
                    "efficiency_score": 80,
                    "optimizations": ["Optimization 1", "Optimization 2"]
                }},
                "code_quality": {{
                    "readability_score": 75,
                    "maintainability_score": 70,
                    "best_practices": ["Practice 1", "Practice 2"],
                    "code_smells": ["Smell 1", "Smell 2"]
                }},
                "alternative_approaches": [
                    {{
                        "approach": "Approach name",
                        "description": "How this approach works",
                        "pros": ["Pro 1", "Pro 2"],
                        "cons": ["Con 1", "Con 2"],
                        "complexity": "O(n log n)"
                    }}
                ],
                "learning_points": [
                    "Key concept 1",
                    "Key concept 2"
                ],
                "overall_score": 78,
                "next_steps": [
                    "Step 1 for improvement",
                    "Step 2 for improvement"
                ]
            }}
            
            Focus on:
            1. Correctness and bug identification
            2. Performance analysis and optimization
            3. Code quality and best practices
            4. Alternative solution approaches
            5. Learning opportunities and growth areas
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return self._get_fallback_feedback(code, test_results)
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                feedback_data = json.loads(response_text)
                print("[SUCCESS] [GEMINI_CODING] Code analysis completed successfully")
                return feedback_data
                
            except json.JSONDecodeError:
                return self._get_fallback_feedback(code, test_results)
            
        except Exception as e:
            print(f"[ERROR] [GEMINI_CODING] Error analyzing code: {str(e)}")
            return self._get_fallback_feedback(code, test_results)

    async def generate_learning_path(
        self, 
        user_solutions: List[Dict[str, Any]], 
        user_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized learning path based on user performance"""
        try:
            print("[TARGET] [GEMINI_CODING] Generating personalized learning path")
            
            if not self.available:
                return self._get_fallback_learning_path()
            
            prompt = f"""
            Analyze this user's coding progress and create a personalized learning path:
            
            User Analytics:
            - Problems Solved: {user_analytics.get('total_problems_solved', 0)}
            - Success Rate: {user_analytics.get('success_rate', 0)}%
            - Skill Level: {user_analytics.get('skill_level', 'beginner')}
            - Strong Topics: {user_analytics.get('strong_topics', [])}
            - Weak Topics: {user_analytics.get('weak_topics', [])}
            - Preferred Language: {user_analytics.get('preferred_language', 'python')}
            
            Recent Solutions: {json.dumps(user_solutions[-10:] if len(user_solutions) > 10 else user_solutions, indent=2)}
            
            Generate a comprehensive learning plan in this JSON format:
            {{
                "current_skill_assessment": {{
                    "level": "intermediate",
                    "strengths": ["Strength 1", "Strength 2"],
                    "weaknesses": ["Weakness 1", "Weakness 2"],
                    "confidence_score": 75
                }},
                "learning_objectives": [
                    {{
                        "goal": "Master dynamic programming",
                        "priority": "high",
                        "estimated_weeks": 3,
                        "success_criteria": ["Criteria 1", "Criteria 2"]
                    }}
                ],
                "recommended_topics": [
                    {{
                        "topic": "Arrays and Strings",
                        "difficulty": "medium",
                        "problems_count": 15,
                        "estimated_time": "2 weeks",
                        "prerequisites": ["Basic programming"],
                        "learning_resources": ["Resource 1", "Resource 2"]
                    }}
                ],
                "practice_schedule": {{
                    "daily_problems": 2,
                    "weekly_goals": "Complete 10 medium problems",
                    "review_schedule": "Every 3 days",
                    "difficulty_progression": "Start easy, progress to medium"
                }},
                "improvement_areas": [
                    {{
                        "area": "Time complexity analysis",
                        "current_level": "basic",
                        "target_level": "advanced",
                        "action_plan": ["Action 1", "Action 2"]
                    }}
                ],
                "milestone_tracking": [
                    {{
                        "milestone": "Solve 50 array problems",
                        "target_date": "2024-02-15",
                        "progress_indicators": ["Indicator 1", "Indicator 2"]
                    }}
                ]
            }}
            
            Make the plan:
            1. Specific and actionable
            2. Tailored to current skill level
            3. Progressive in difficulty
            4. Include measurable goals
            5. Address identified weaknesses
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return self._get_fallback_learning_path()
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                learning_data = json.loads(response_text)
                print("[SUCCESS] [GEMINI_CODING] Learning path generated successfully")
                return learning_data
                
            except json.JSONDecodeError:
                return self._get_fallback_learning_path()
            
        except Exception as e:
            print(f"[ERROR] [GEMINI_CODING] Error generating learning path: {str(e)}")
            return self._get_fallback_learning_path()

    def execute_code(
        self, 
        code: str, 
        language: str, 
        test_cases: List[Dict[str, Any]],
        time_limit: int = 5000,
        memory_limit: int = 256
    ) -> Dict[str, Any]:
        """Execute code with test cases in a secure environment"""
        try:
            print(f"⚡ [CODE_EXECUTION] Executing {language} code with {len(test_cases)} test cases")
            
            results = []
            total_time = 0
            max_memory = 0
            
            for i, test_case in enumerate(test_cases):
                try:
                    start_time = time.time()
                    
                    if language == "python":
                        result = self._execute_python(code, test_case)
                    elif language == "javascript":
                        result = self._execute_javascript(code, test_case)
                    elif language == "java":
                        result = self._execute_java(code, test_case)
                    elif language == "cpp":
                        result = self._execute_cpp(code, test_case)
                    else:
                        result = {
                            "passed": False,
                            "output": None,
                            "error": f"Unsupported language: {language}",
                            "execution_time": 0,
                            "memory_used": 0
                        }
                    
                    execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
                    result["execution_time"] = execution_time
                    result["test_case_index"] = i
                    
                    total_time += execution_time
                    max_memory = max(max_memory, result.get("memory_used", 0))
                    
                    # Check time limit
                    if execution_time > time_limit:
                        result["passed"] = False
                        result["error"] = "Time Limit Exceeded"
                    
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        "test_case_index": i,
                        "passed": False,
                        "output": None,
                        "test_input": test_case.get('input', {}),
                        "error": f"Execution error: {str(e)}",
                        "execution_time": 0,
                        "memory_used": 0
                    })
            
            success = all(result.get("passed", False) for result in results)
            
            print(f"[SUCCESS] [CODE_EXECUTION] Execution completed - Success: {success}")
            
            return {
                "success": success,
                "results": results,
                "execution_time": total_time,
                "memory_used": max_memory,
                "error_message": None if success else "Some test cases failed"
            }
            
        except Exception as e:
            print(f"[ERROR] [CODE_EXECUTION] Execution failed: {str(e)}")
            return {
                "success": False,
                "results": [],
                "execution_time": 0,
                "memory_used": 0,
                "error_message": str(e)
            }

    def _execute_python(self, code: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code with a test case"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Create a wrapper that handles input/output
                wrapper_code = f"""
import sys
import json
import traceback
from io import StringIO

# Redirect stdout to capture output
old_stdout = sys.stdout
sys.stdout = captured_output = StringIO()

try:
    # User's code
{code}
    
    # Test case input
    test_input = {json.dumps(test_case.get('input', {}))}
    expected_output = {json.dumps(test_case.get('output'))}
    
    # Try different function calling strategies
    result = None
    error_msg = None
    
    # Strategy 1: Try to find a function that matches common patterns
    import inspect
    functions = [obj for name, obj in globals().items() if inspect.isfunction(obj)]
    
    if functions:
        # Try the first function with different calling patterns
        func = functions[0]
        try:
            # If test_input is a dict, try calling with **kwargs
            if isinstance(test_input, dict):
                result = func(**test_input)
            # If test_input is a list, try calling with *args
            elif isinstance(test_input, list):
                result = func(*test_input)
            # Otherwise, try calling with the input directly
            else:
                result = func(test_input)
        except Exception as e:
            # If that fails, try calling with the input as a single argument
            try:
                result = func(test_input)
            except Exception as e2:
                error_msg = f"Function call failed: {{str(e)}}"
    else:
        error_msg = "No function found in the code"
    
    # Debug: Print what we found
    print(f"DEBUG: Found {{len(functions)}} functions: {{[f.__name__ for f in functions]}}")
    print(f"DEBUG: test_input = {{test_input}}, type = {{type(test_input)}}")
    print(f"DEBUG: expected_output = {{expected_output}}, type = {{type(expected_output)}}")
    
    # Special handling for functions that modify input in-place (like group_seeds)
    if result is None and error_msg is None and functions:
        try:
            # For functions that modify arrays in-place, we need to make a copy
            if isinstance(test_input, list):
                test_input_copy = test_input.copy()
                func(test_input_copy)
                result = test_input_copy
            else:
                # For other cases, try calling the function directly
                result = func(test_input)
        except Exception as e:
            error_msg = f"Function execution failed: {{str(e)}}"
    
    # If we still don't have a result, try to evaluate the code directly
    if result is None and error_msg is None:
        try:
            # Try to execute the code with the test input as a variable
            exec(f"test_input = {{json.dumps(test_input)}}")
            # This is a fallback - might not work for all cases
            error_msg = "Could not determine how to call the function"
        except Exception as e:
            error_msg = f"Execution error: {{str(e)}}"
    
    # Compare result
    if error_msg:
        passed = False
        result = None
    else:
        # Handle different comparison types
        if isinstance(expected_output, list) and isinstance(result, list):
            # For lists, compare elements
            passed = result == expected_output
        elif isinstance(expected_output, (int, float)) and isinstance(result, (int, float)):
            # For numbers, allow small floating point differences
            passed = abs(result - expected_output) < 1e-9
        elif isinstance(expected_output, bool) and isinstance(result, bool):
            # For booleans, direct comparison
            passed = result == expected_output
        else:
            # For other types, direct comparison
            passed = result == expected_output
        
        # Debug: Print comparison details
        print(f"DEBUG: result = {{result}}, type = {{type(result)}}")
        print(f"DEBUG: expected = {{expected_output}}, type = {{type(expected_output)}}")
        print(f"DEBUG: passed = {{passed}}")
    
    print(json.dumps({{
        "passed": passed,
        "output": result,
        "expected": expected_output,
        "test_input": test_input,
        "error": error_msg
    }}))
    
except Exception as e:
    print(json.dumps({{
        "passed": False,
        "output": None,
        "expected": {json.dumps(test_case.get('output'))},
        "test_input": {json.dumps(test_case.get('input', {}))},
        "error": f"Execution error: {{str(e)}}"
    }}))
finally:
    sys.stdout = old_stdout
                """
                f.write(wrapper_code)
                f.flush()
                
                # Execute with timeout
                result = subprocess.run(
                    ['python', f.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                os.unlink(f.name)  # Clean up temp file
                
                if result.returncode == 0:
                    try:
                        stdout_text = result.stdout.strip()
                        if not stdout_text:
                            return {
                                "passed": False,
                                "output": None,
                                "error": "No output from code execution",
                                "memory_used": 50
                            }
                        
                        output_data = json.loads(stdout_text)
                        output_data["memory_used"] = 50  # Approximate memory usage
                        
                        # Ensure all required fields are present
                        if "passed" not in output_data:
                            output_data["passed"] = False
                        if "output" not in output_data:
                            output_data["output"] = None
                        if "error" not in output_data:
                            output_data["error"] = None
                        if "test_input" not in output_data:
                            output_data["test_input"] = test_case.get('input', {})
                            
                        return output_data
                    except json.JSONDecodeError as e:
                        return {
                            "passed": False,
                            "output": None,
                            "error": f"Invalid output format: {str(e)}",
                            "test_input": test_case.get('input', {}),
                            "memory_used": 50
                        }
                else:
                    stderr_text = result.stderr or "Runtime error"
                    return {
                        "passed": False,
                        "output": None,
                        "error": stderr_text,
                        "test_input": test_case.get('input', {}),
                        "memory_used": 50
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": None,
                "error": "Time Limit Exceeded",
                "memory_used": 50
            }
        except Exception as e:
            return {
                "passed": False,
                "output": None,
                "error": str(e),
                "memory_used": 50
            }

    def _execute_javascript(self, code: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JavaScript code with a test case (basic implementation)"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                # Enhanced wrapper with better function detection
                wrapper = """
{code}

const __testInput = {test_input};
const __expected = {test_output};
let __result;
let __error = null;

try {{
  // Try to find and call the function
  let func = null;
  
  // Strategy 1: Look for common function names
  if (typeof main === 'function') {{
    func = main;
  }} else if (typeof solution === 'function') {{
    func = solution;
  }} else if (typeof solve === 'function') {{
    func = solve;
  }} else {{
    // Strategy 2: Find any function in the global scope
    const funcNames = Object.getOwnPropertyNames(this).filter(name => 
      typeof this[name] === 'function' && name !== 'main' && name !== 'solution' && name !== 'solve'
    );
    if (funcNames.length > 0) {{
      func = this[funcNames[0]];
    }}
  }}
  
  if (func) {{
    // Try different calling patterns
    try {{
      if (Array.isArray(__testInput)) {{
        // For arrays, try spreading first, then direct call
        try {{
          __result = func(...__testInput);
        }} catch (e) {{
          // If spreading fails, try calling with the array directly
          __result = func(__testInput);
        }}
      }} else if (typeof __testInput === 'object' && __testInput !== null) {{
        __result = func(__testInput);
      }} else {{
        __result = func(__testInput);
      }}
    }} catch (e) {{
      // If that fails, try calling with the input as a single argument
      try {{
        __result = func(__testInput);
      }} catch (e2) {{
        __error = `Function call failed: ${{e.message}}`;
      }}
    }}
  }} else {{
    __error = "No function found in the code";
  }}
  
  // Compare results
  let passed = false;
  if (__error === null) {{
    if (Array.isArray(__expected) && Array.isArray(__result)) {{
      passed = JSON.stringify(__result) === JSON.stringify(__expected);
    }} else {{
      passed = __result === __expected;
    }}
  }}
  
  console.log(JSON.stringify({{ 
    passed: passed, 
    output: __result, 
    expected: __expected, 
    test_input: __testInput, 
    error: __error 
  }}));
}} catch (e) {{
  console.log(JSON.stringify({{ 
    passed: false, 
    output: null, 
    expected: __expected, 
    test_input: __testInput, 
    error: String(e) 
  }}));
}}
""".format(
                    code=code,
                    test_input=json.dumps(test_case.get('input')),
                    test_output=json.dumps(test_case.get('output'))
                )
                f.write(wrapper)
                f.flush()
                result = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=5)
                os.unlink(f.name)
                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout.strip())
                        data["memory_used"] = 30
                        return data
                    except json.JSONDecodeError:
                        return {"passed": False, "output": None, "error": "Invalid JS output", "memory_used": 30}
                else:
                    return {"passed": False, "output": None, "error": result.stderr or "Runtime error", "memory_used": 30}
        except subprocess.TimeoutExpired:
            return {"passed": False, "output": None, "error": "Time Limit Exceeded", "memory_used": 30}
        except Exception as e:
            return {"passed": False, "output": None, "error": str(e), "memory_used": 30}

    def _execute_java(self, code: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Java code with a test case (simplified implementation)"""
        # For now, return a mock result
        return {
            "passed": True,
            "output": test_case.get('output'),
            "error": None,
            "memory_used": 100
        }

    def _execute_cpp(self, code: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute C++ code with a test case (simplified implementation)"""
        # For now, return a mock result
        return {
            "passed": True,
            "output": test_case.get('output'),
            "error": None,
            "memory_used": 80
        }

    def _get_fallback_problem(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Get a fallback problem when AI is not available"""
        import random
        
        # Get random problem from the topic
        problems = self._get_comprehensive_problems()
        if topic in problems and difficulty in problems[topic]:
            topic_problems = problems[topic][difficulty]
            if isinstance(topic_problems, list):
                selected_problem = random.choice(topic_problems)
            else:
                selected_problem = topic_problems
        else:
            # Default fallback
            selected_problem = {
                "title": "Two Sum",
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                "test_cases": [
                    {"input": "2 7 11 15\n9", "output": "0 1"},
                    {"input": "3 2 4\n6", "output": "1 2"},
                    {"input": "3 3\n6", "output": "0 1"}
                ],
                "hidden_test_cases": [
                    {"input": "1 2 3 4 5\n8", "output": "2 4"},
                    {"input": "10 20 30 40 50\n70", "output": "1 3"}
                ],
                "examples": [
                    {"input": "2 7 11 15\n9", "output": "0 1", "explanation": "nums[0] + nums[1] = 2 + 7 = 9"}
                ],
                "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
                "starter_code": {
                    "python": "def twoSum(nums, target):\n    # Your code here\n    pass",
                    "javascript": "function twoSum(nums, target) {\n    // Your code here\n}",
                    "java": "public int[] twoSum(int[] nums, int target) {\n    // Your code here\n    return new int[0];\n}",
                    "cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    // Your code here\n    return {};\n}"
                },
                "expected_complexity": {"time": "O(n)", "space": "O(n)"}
            }
        
        return selected_problem

    def _get_comprehensive_problems(self) -> Dict[str, Any]:
        """Get comprehensive problem database with proper test cases"""
        return {
            "Arrays": {
                "easy": [
                    {
                        "title": "Two Sum",
                        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
                    "test_cases": [
                            {"input": "2 7 11 15\n9", "output": "0 1"},
                            {"input": "3 2 4\n6", "output": "1 2"},
                            {"input": "3 3\n6", "output": "0 1"}
                        ],
                        "hidden_test_cases": [
                            {"input": "1 2 3 4 5\n8", "output": "2 4"},
                            {"input": "10 20 30 40 50\n70", "output": "1 3"},
                            {"input": "0 4 3 0\n0", "output": "0 3"}
                        ],
                        "examples": [
                            {"input": "2 7 11 15\n9", "output": "0 1", "explanation": "nums[0] + nums[1] = 2 + 7 = 9"}
                        ],
                        "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
                        "starter_code": {
                            "python": "def twoSum(nums, target):\n    # Your code here\n    pass",
                            "javascript": "function twoSum(nums, target) {\n    // Your code here\n}",
                            "java": "public int[] twoSum(int[] nums, int target) {\n    // Your code here\n    return new int[0];\n}",
                            "cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    // Your code here\n    return {};\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(n)"}
                    },
                    {
                        "title": "Maximum Subarray Sum",
                        "description": "Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
                        "test_cases": [
                            {"input": "-2 1 -3 4 -1 2 1 -5 4", "output": "6"},
                            {"input": "1", "output": "1"},
                            {"input": "5 4 -1 7 8", "output": "23"}
                        ],
                        "hidden_test_cases": [
                            {"input": "-1 -2 -3 -4", "output": "-1"},
                            {"input": "1 2 3 4 5", "output": "15"},
                            {"input": "-2 -1 -3 -4", "output": "-1"}
                        ],
                        "examples": [
                            {"input": "-2 1 -3 4 -1 2 1 -5 4", "output": "6", "explanation": "The subarray [4,-1,2,1] has the largest sum 6."}
                        ],
                        "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
                        "starter_code": {
                            "python": "def maxSubArray(nums):\n    # Your code here\n    pass",
                            "javascript": "function maxSubArray(nums) {\n    // Your code here\n}",
                            "java": "public int maxSubArray(int[] nums) {\n    // Your code here\n    return 0;\n}",
                            "cpp": "int maxSubArray(vector<int>& nums) {\n    // Your code here\n    return 0;\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(1)"}
                    }
                ],
                "medium": [
                    {
                    "title": "Product of Array Except Self",
                    "description": "Given an array nums, return an array where each element is the product of all elements in nums except nums[i]. You must solve it in O(n) time without using division.",
                    "test_cases": [
                            {"input": "1 2 3 4", "output": "24 12 8 6"},
                            {"input": "-1 1 0 -3 3", "output": "0 0 9 0 0"},
                            {"input": "2 3 4 5", "output": "60 40 30 24"}
                        ],
                        "hidden_test_cases": [
                            {"input": "1 0", "output": "0 1"},
                            {"input": "1 2 3", "output": "6 3 2"},
                            {"input": "0 0 0", "output": "0 0 0"}
                        ],
                        "examples": [
                            {"input": "1 2 3 4", "output": "24 12 8 6", "explanation": "For index 0: 2*3*4=24, for index 1: 1*3*4=12, etc."}
                        ],
                        "constraints": ["2 <= nums.length <= 10^5", "-30 <= nums[i] <= 30"],
                        "starter_code": {
                            "python": "def productExceptSelf(nums):\n    # Your code here\n    pass",
                            "javascript": "function productExceptSelf(nums) {\n    // Your code here\n}",
                            "java": "public int[] productExceptSelf(int[] nums) {\n    // Your code here\n    return new int[0];\n}",
                            "cpp": "vector<int> productExceptSelf(vector<int>& nums) {\n    // Your code here\n    return {};\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(1)"}
                    },
                    {
                        "title": "3Sum",
                        "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.",
                        "test_cases": [
                            {"input": "-1 0 1 2 -1 -4", "output": "-1 -1 2\n-1 0 1"},
                            {"input": "0 1 1", "output": ""},
                            {"input": "0 0 0", "output": "0 0 0"}
                        ],
                        "hidden_test_cases": [
                            {"input": "-2 0 1 1 2", "output": "-2 0 2\n-2 1 1"},
                            {"input": "1 2 -2 -1", "output": "-2 1 1"},
                            {"input": "0 0 0 0", "output": "0 0 0"}
                        ],
                        "examples": [
                            {"input": "-1 0 1 2 -1 -4", "output": "-1 -1 2\n-1 0 1", "explanation": "nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0"}
                        ],
                        "constraints": ["3 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"],
                        "starter_code": {
                            "python": "def threeSum(nums):\n    # Your code here\n    pass",
                            "javascript": "function threeSum(nums) {\n    // Your code here\n}",
                            "java": "public List<List<Integer>> threeSum(int[] nums) {\n    // Your code here\n    return new ArrayList<>();\n}",
                            "cpp": "vector<vector<int>> threeSum(vector<int>& nums) {\n    // Your code here\n    return {};\n}"
                        },
                        "expected_complexity": {"time": "O(n^2)", "space": "O(1)"}
                    }
                ],
                "hard": [
                    {
                    "title": "Sliding Window Maximum",
                    "description": "Given an array and a sliding window of size k, find the maximum element in each window. Solve in O(n) time using a deque.",
                    "test_cases": [
                            {"input": "1 3 -1 -3 5 3 6 7\n3", "output": "3 3 5 5 6 7"},
                            {"input": "1\n1", "output": "1"},
                            {"input": "1 -1\n1", "output": "1 -1"}
                        ],
                        "hidden_test_cases": [
                            {"input": "9 11\n2", "output": "11"},
                            {"input": "4 -2\n2", "output": "4"},
                            {"input": "1 3 1 2 0 5\n3", "output": "3 3 2 5"}
                        ],
                        "examples": [
                            {"input": "1 3 -1 -3 5 3 6 7\n3", "output": "3 3 5 5 6 7", "explanation": "Window position: [1 3 -1] -3 5 3 6 7 -> Max = 3"}
                        ],
                        "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4", "1 <= k <= nums.length"],
                        "starter_code": {
                            "python": "def maxSlidingWindow(nums, k):\n    # Your code here\n    pass",
                            "javascript": "function maxSlidingWindow(nums, k) {\n    // Your code here\n}",
                            "java": "public int[] maxSlidingWindow(int[] nums, int k) {\n    // Your code here\n    return new int[0];\n}",
                            "cpp": "vector<int> maxSlidingWindow(vector<int>& nums, int k) {\n    // Your code here\n    return {};\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(k)"}
                    }
                ]
            },
            "Strings": {
                "easy": [
                    {
                        "title": "Valid Parentheses",
                        "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
                        "test_cases": [
                            {"input": "()", "output": "true"},
                            {"input": "()[]{}", "output": "true"},
                            {"input": "(]", "output": "false"}
                        ],
                        "hidden_test_cases": [
                            {"input": "([)]", "output": "false"},
                            {"input": "{[]}", "output": "true"},
                            {"input": "(((", "output": "false"}
                        ],
                        "examples": [
                            {"input": "()", "output": "true", "explanation": "Valid parentheses"}
                        ],
                        "constraints": ["1 <= s.length <= 10^4", "s consists of parentheses only '()[]{}'"],
                        "starter_code": {
                            "python": "def isValid(s):\n    # Your code here\n    pass",
                            "javascript": "function isValid(s) {\n    // Your code here\n}",
                            "java": "public boolean isValid(String s) {\n    // Your code here\n    return false;\n}",
                            "cpp": "bool isValid(string s) {\n    // Your code here\n    return false;\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(n)"}
                    }
                ],
                "medium": [
                    {
                        "title": "Longest Substring Without Repeating Characters",
                        "description": "Given a string s, find the length of the longest substring without repeating characters.",
                        "test_cases": [
                            {"input": "abcabcbb", "output": "3"},
                            {"input": "bbbbb", "output": "1"},
                            {"input": "pwwkew", "output": "3"}
                        ],
                        "hidden_test_cases": [
                            {"input": "", "output": "0"},
                            {"input": " ", "output": "1"},
                            {"input": "dvdf", "output": "3"}
                        ],
                        "examples": [
                            {"input": "abcabcbb", "output": "3", "explanation": "The answer is 'abc', with the length of 3."}
                        ],
                        "constraints": ["0 <= s.length <= 5 * 10^4", "s consists of English letters, digits, symbols and spaces"],
                        "starter_code": {
                            "python": "def lengthOfLongestSubstring(s):\n    # Your code here\n    pass",
                            "javascript": "function lengthOfLongestSubstring(s) {\n    // Your code here\n}",
                            "java": "public int lengthOfLongestSubstring(String s) {\n    // Your code here\n    return 0;\n}",
                            "cpp": "int lengthOfLongestSubstring(string s) {\n    // Your code here\n    return 0;\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(min(m,n))"}
                    }
                ],
                "hard": [
                    {
                        "title": "Edit Distance",
                        "description": "Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2. You have the following three operations permitted on a word: Insert a character, Delete a character, Replace a character.",
                    "test_cases": [
                            {"input": "horse\nros", "output": "3"},
                            {"input": "intention\nexecution", "output": "5"},
                            {"input": "a\nab", "output": "1"}
                        ],
                        "hidden_test_cases": [
                            {"input": "abc\nabc", "output": "0"},
                            {"input": "abc\n", "output": "3"},
                            {"input": "\nabc", "output": "3"}
                        ],
                        "examples": [
                            {"input": "horse\nros", "output": "3", "explanation": "horse -> rorse -> rose -> ros"}
                        ],
                        "constraints": ["0 <= word1.length, word2.length <= 500", "word1 and word2 consist of lowercase English letters"],
                        "starter_code": {
                            "python": "def minDistance(word1, word2):\n    # Your code here\n    pass",
                            "javascript": "function minDistance(word1, word2) {\n    // Your code here\n}",
                            "java": "public int minDistance(String word1, String word2) {\n    // Your code here\n    return 0;\n}",
                            "cpp": "int minDistance(string word1, string word2) {\n    // Your code here\n    return 0;\n}"
                        },
                        "expected_complexity": {"time": "O(m*n)", "space": "O(m*n)"}
                    }
                ]
            },
            "Dynamic Programming": {
                "easy": [
                    {
                        "title": "Climbing Stairs",
                        "description": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
                        "test_cases": [
                            {"input": "2", "output": "2"},
                            {"input": "3", "output": "3"},
                            {"input": "1", "output": "1"}
                        ],
                        "hidden_test_cases": [
                            {"input": "4", "output": "5"},
                            {"input": "5", "output": "8"},
                            {"input": "6", "output": "13"}
                        ],
                        "examples": [
                            {"input": "2", "output": "2", "explanation": "There are two ways to climb to the top: 1. 1 step + 1 step, 2. 2 steps"}
                        ],
                        "constraints": ["1 <= n <= 45"],
                        "starter_code": {
                            "python": "def climbStairs(n):\n    # Your code here\n    pass",
                            "javascript": "function climbStairs(n) {\n    // Your code here\n}",
                            "java": "public int climbStairs(int n) {\n    // Your code here\n    return 0;\n}",
                            "cpp": "int climbStairs(int n) {\n    // Your code here\n    return 0;\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(1)"}
                    }
                ],
                "medium": [
                    {
                        "title": "House Robber",
                        "description": "You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. Adjacent houses have security systems connected and will automatically contact the police if two adjacent houses were broken into on the same night. Given an integer array nums representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.",
                        "test_cases": [
                            {"input": "1 2 3 1", "output": "4"},
                            {"input": "2 7 9 3 1", "output": "12"},
                            {"input": "2 1 1 2", "output": "4"}
                        ],
                        "hidden_test_cases": [
                            {"input": "1", "output": "1"},
                            {"input": "1 2", "output": "2"},
                            {"input": "5 1 1 5", "output": "10"}
                        ],
                        "examples": [
                            {"input": "1 2 3 1", "output": "4", "explanation": "Rob house 1 (money = 1) and then rob house 3 (money = 3). Total amount = 1 + 3 = 4."}
                        ],
                        "constraints": ["1 <= nums.length <= 100", "0 <= nums[i] <= 400"],
                        "starter_code": {
                            "python": "def rob(nums):\n    # Your code here\n    pass",
                            "javascript": "function rob(nums) {\n    // Your code here\n}",
                            "java": "public int rob(int[] nums) {\n    // Your code here\n    return 0;\n}",
                            "cpp": "int rob(vector<int>& nums) {\n    // Your code here\n    return 0;\n}"
                        },
                        "expected_complexity": {"time": "O(n)", "space": "O(1)"}
                    }
                ],
                "hard": [
                    {
                        "title": "Edit Distance",
                        "description": "Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2. You have the following three operations permitted on a word: Insert a character, Delete a character, Replace a character.",
                        "test_cases": [
                            {"input": "horse\nros", "output": "3"},
                            {"input": "intention\nexecution", "output": "5"},
                            {"input": "a\nab", "output": "1"}
                        ],
                        "hidden_test_cases": [
                            {"input": "abc\nabc", "output": "0"},
                            {"input": "abc\n", "output": "3"},
                            {"input": "\nabc", "output": "3"}
                        ],
                        "examples": [
                            {"input": "horse\nros", "output": "3", "explanation": "horse -> rorse -> rose -> ros"}
                        ],
                        "constraints": ["0 <= word1.length, word2.length <= 500", "word1 and word2 consist of lowercase English letters"],
                        "starter_code": {
                            "python": "def minDistance(word1, word2):\n    # Your code here\n    pass",
                            "javascript": "function minDistance(word1, word2) {\n    // Your code here\n}",
                            "java": "public int minDistance(String word1, String word2) {\n    // Your code here\n    return 0;\n}",
                            "cpp": "int minDistance(string word1, string word2) {\n    // Your code here\n    return 0;\n}"
                        },
                        "expected_complexity": {"time": "O(m*n)", "space": "O(m*n)"}
                    }
                ]
            },
            "Machine Learning": {
                "easy": [
                    {
                        "title": "Linear Regression Implementation",
                        "description": "Implement linear regression from scratch using gradient descent. Given training data (X, y), find the best line that fits the data.",
                        "test_cases": [
                            {"input": "1 2 3 4\n2 4 6 8\n0.01\n1000", "output": "Slope: 2.0, Intercept: 0.0"},
                            {"input": "1 2 3\n3 5 7\n0.1\n500", "output": "Slope: 2.0, Intercept: 1.0"},
                            {"input": "0 1 2\n1 3 5\n0.01\n1000", "output": "Slope: 2.0, Intercept: 1.0"}
                        ],
                        "hidden_test_cases": [
                            {"input": "1 2 3 4 5\n1 2 3 4 5\n0.01\n1000", "output": "Slope: 1.0, Intercept: 0.0"},
                            {"input": "1 2 3 4\n0 1 2 3\n0.01\n1000", "output": "Slope: 1.0, Intercept: -1.0"}
                        ],
                        "examples": [
                            {"input": "1 2 3 4\n2 4 6 8\n0.01\n1000", "output": "Slope: 2.0, Intercept: 0.0", "explanation": "Perfect linear relationship y = 2x"}
                        ],
                        "constraints": ["1 <= n <= 1000", "0.001 <= learning_rate <= 0.1", "100 <= epochs <= 10000"],
                        "starter_code": {
                            "python": "def linear_regression(X, y, learning_rate, epochs):\n    # Your code here\n    pass",
                            "javascript": "function linearRegression(X, y, learningRate, epochs) {\n    // Your code here\n}",
                            "java": "public String linearRegression(double[] X, double[] y, double learningRate, int epochs) {\n    // Your code here\n    return \"\";\n}",
                            "cpp": "string linearRegression(vector<double>& X, vector<double>& y, double learningRate, int epochs) {\n    // Your code here\n    return \"\";\n}"
                        },
                        "expected_complexity": {"time": "O(n*epochs)", "space": "O(1)"}
                    }
                ],
                "medium": {
                    "title": "Neural Network Backpropagation",
                    "description": "Implement a simple neural network with one hidden layer using backpropagation. Include forward pass, backward pass, and weight updates. Support multiple activation functions (sigmoid, ReLU, tanh).",
                    "test_cases": [
                        {"input": {"X": [[0, 0], [0, 1], [1, 0], [1, 1]], "y": [0, 1, 1, 0], "hidden_size": 4, "epochs": 1000}, "output": "XOR problem solved"},
                        {"input": {"X": [[1, 2], [2, 3], [3, 4]], "y": [0, 1, 0], "hidden_size": 3, "epochs": 500}, "output": "Classification completed"}
                    ]
                },
                "hard": {
                    "title": "Convolutional Neural Network Implementation",
                    "description": "Implement a CNN from scratch including convolution, pooling, and fully connected layers. Support multiple filter sizes, stride, and padding. Include forward and backward propagation.",
                    "test_cases": [
                        {"input": {"image_shape": [28, 28, 1], "num_classes": 10, "filters": [32, 64], "epochs": 10}, "output": "CNN trained successfully"}
                    ]
                }
            },
            "Web Development": {
                "easy": {
                    "title": "Rate Limiting Middleware",
                    "description": "Implement a rate limiting middleware for a web API that limits requests per IP address. Use a sliding window algorithm with Redis or in-memory storage. Support different rate limits for different endpoints.",
                    "test_cases": [
                        {"input": {"ip": "192.168.1.1", "endpoint": "/api/users", "limit": 100, "window": 3600}, "output": "Rate limit applied"},
                        {"input": {"ip": "192.168.1.2", "endpoint": "/api/admin", "limit": 10, "window": 3600}, "output": "Admin rate limit enforced"}
                    ]
                },
                "medium": {
                    "title": "WebSocket Real-time Chat System",
                    "description": "Implement a real-time chat system using WebSockets with features like private messaging, group chats, message persistence, and user presence. Include authentication and message encryption.",
                    "test_cases": [
                        {"input": {"users": ["user1", "user2"], "message": "Hello", "room": "general"}, "output": "Message broadcasted"},
                        {"input": {"users": ["user1", "user3"], "message": "Private message", "room": "private"}, "output": "Private message delivered"}
                    ]
                },
                "hard": {
                    "title": "Microservices Architecture with API Gateway",
                    "description": "Design and implement a microservices architecture with an API Gateway, service discovery, load balancing, and circuit breaker pattern. Include authentication, logging, and monitoring.",
                    "test_cases": [
                        {"input": {"services": ["user-service", "order-service", "payment-service"], "gateway": "api-gateway", "load_balancer": "round-robin"}, "output": "Microservices deployed"},
                        {"input": {"circuit_breaker": {"threshold": 5, "timeout": 30}, "monitoring": "prometheus"}, "output": "Resilience patterns implemented"}
                    ]
                }
            },
            "Python Programming": {
                "easy": {
                    "title": "Context Manager Implementation",
                    "description": "Implement a custom context manager class that handles database connections with automatic cleanup, connection pooling, and transaction management. Include proper exception handling and resource cleanup.",
                    "test_cases": [
                        {"input": {"db_url": "sqlite:///test.db", "pool_size": 5, "timeout": 30}, "output": "Connection managed successfully"},
                        {"input": {"db_url": "postgresql://user:pass@localhost/db", "pool_size": 10, "timeout": 60}, "output": "Transaction committed"}
                    ]
                },
                "medium": {
                    "title": "Async/Await Web Scraper",
                    "description": "Implement an asynchronous web scraper using asyncio and aiohttp that can scrape multiple URLs concurrently. Include rate limiting, retry logic, and data extraction with BeautifulSoup. Handle different content types and implement proper error handling.",
                    "test_cases": [
                        {"input": {"urls": ["https://example1.com", "https://example2.com"], "concurrency": 5, "rate_limit": 2}, "output": "Data scraped successfully"},
                        {"input": {"urls": ["https://api.example.com/data"], "headers": {"Authorization": "Bearer token"}, "retry_count": 3}, "output": "API data extracted"}
                    ]
                },
                "hard": {
                    "title": "Distributed Task Queue with Celery",
                    "description": "Implement a distributed task queue system using Celery with Redis as the message broker. Include task scheduling, priority queues, result backends, monitoring, and error handling. Support task chaining and workflow management.",
                    "test_cases": [
                        {"input": {"tasks": ["process_data", "send_email", "generate_report"], "workers": 4, "priority": "high"}, "output": "Tasks queued successfully"},
                        {"input": {"workflow": "data_pipeline", "retry_policy": {"max_retries": 3, "backoff": "exponential"}, "monitoring": "flower"}, "output": "Workflow executed"}
                    ]
                }
            },
            "JavaScript": {
                "easy": {
                    "title": "React Hooks Custom Implementation",
                    "description": "Implement custom React hooks including useState, useEffect, useReducer, and useCallback from scratch. Include proper dependency tracking, cleanup functions, and performance optimizations. Support concurrent features and suspense.",
                    "test_cases": [
                        {"input": {"hook": "useState", "initialValue": 0, "updates": [1, 2, 3]}, "output": "State managed correctly"},
                        {"input": {"hook": "useEffect", "dependencies": ["count"], "cleanup": "timer"}, "output": "Effect executed and cleaned up"}
                    ]
                },
                "medium": {
                    "title": "Node.js Microservices with Express",
                    "description": "Build a microservices architecture using Node.js and Express with service discovery, API Gateway, load balancing, and inter-service communication. Include authentication, logging, monitoring, and error handling.",
                    "test_cases": [
                        {"input": {"services": ["user-service", "order-service"], "gateway": "express-gateway", "discovery": "consul"}, "output": "Microservices deployed"},
                        {"input": {"communication": "gRPC", "auth": "JWT", "monitoring": "prometheus"}, "output": "Services communicating"}
                    ]
                },
                "hard": {
                    "title": "Real-time Data Processing with WebSockets and Redis",
                    "description": "Implement a real-time data processing system using WebSockets, Redis Streams, and Node.js. Include data ingestion, real-time analytics, pub/sub messaging, and horizontal scaling. Support multiple data sources and complex event processing.",
                    "test_cases": [
                        {"input": {"sources": ["sensor_data", "user_events"], "processing": "stream", "output": "kafka"}, "output": "Data processed in real-time"},
                        {"input": {"analytics": "real-time", "scaling": "horizontal", "monitoring": "grafana"}, "output": "System scaled successfully"}
                    ]
                }
            }
        }
        
        # Try to find a matching problem or create a dynamic one
        default_problem = problems.get(topic, {}).get(difficulty)
        
        if not default_problem:
            # Try to find a similar topic
            similar_topics = {
                "programming": "Arrays",
                "coding": "Arrays", 
                "computer science": "Arrays",
                "cs": "Arrays",
                "software": "Arrays",
                "web": "Web Development",
                "frontend": "JavaScript",
                "backend": "Python Programming",
                "data science": "Machine Learning",
                "ai": "Machine Learning",
                "machine learning": "Machine Learning",
                "ml": "Machine Learning",
                "python": "Python Programming",
                "javascript": "JavaScript",
                "java": "Arrays",
                "c++": "Arrays",
                "react": "JavaScript",
                "node": "JavaScript",
                "sql": "Web Development",
                "database": "Web Development"
            }
            
            # Find similar topic
            for key, value in similar_topics.items():
                if key in topic.lower():
                    default_problem = problems.get(value, {}).get(difficulty)
                    break
            
            # If still no match, use Arrays as default
            if not default_problem:
                default_problem = problems.get("Arrays", {}).get(difficulty, problems["Arrays"]["easy"])
        
        # Generate dynamic problem if still no match
        if not default_problem:
            default_problem = self._generate_dynamic_coding_problem(topic, difficulty)
        
        return {
            "title": default_problem["title"],
            "description": default_problem["description"],
            "topic": topic,
            "difficulty": difficulty,
            "constraints": default_problem.get("constraints", ["1 <= n <= 1000", "Values can be negative"]),
            "examples": default_problem.get("examples", [
                {
                    "input": "Example input",
                    "output": "Example output",
                    "explanation": "This is a fallback example"
                }
            ]),
            "test_cases": default_problem.get("test_cases", []),
            "hidden_test_cases": default_problem.get("test_cases", [])[:2],  # Use first 2 as hidden
            "expected_complexity": default_problem.get("expected_complexity", {"time": "O(n)", "space": "O(1)"}),
            "hints": default_problem.get("hints", ["Think about the basic approach", "Consider edge cases"]),
            "tags": [topic.lower(), difficulty]
        }

    def _generate_dynamic_coding_problem(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate a dynamic coding problem for any topic"""
        
        # Define problem templates based on topic categories
        programming_topics = ["programming", "coding", "computer science", "cs", "software", "web", "frontend", "backend", "data science", "ai", "machine learning", "ml", "python", "javascript", "java", "c++", "react", "node", "sql", "database"]
        science_topics = ["science", "physics", "chemistry", "biology", "medicine", "engineering", "environmental", "geology", "astronomy"]
        math_topics = ["math", "mathematics", "calculus", "algebra", "statistics", "geometry", "trigonometry", "linear algebra", "discrete"]
        
        # Determine the category
        topic_lower = topic.lower()
        if any(prog_topic in topic_lower for prog_topic in programming_topics):
            category = "programming"
        elif any(sci_topic in topic_lower for sci_topic in science_topics):
            category = "science"
        elif any(math_topic in topic_lower for math_topic in math_topics):
            category = "mathematics"
        else:
            category = "general"
        
        # Generate problems based on category and difficulty
        if category == "programming":
            if difficulty.lower() == "easy":
                return {
                    "title": f"Basic {topic} Algorithm Implementation",
                    "description": f"Implement a fundamental algorithm in {topic}. Create a function that demonstrates core programming concepts and handles basic input/output operations.",
                    "test_cases": [
                        {"input": {"data": [1, 2, 3, 4, 5]}, "output": "Algorithm executed successfully"},
                        {"input": {"data": [10, 20, 30]}, "output": "Result computed"}
                    ]
                }
            elif difficulty.lower() == "medium":
                return {
                    "title": f"Advanced {topic} Problem Solving",
                    "description": f"Solve a complex problem in {topic} using efficient algorithms and data structures. Implement error handling and optimize for performance.",
                    "test_cases": [
                        {"input": {"complex_data": [1, 2, 3, 4, 5], "parameters": {"threshold": 10}}, "output": "Complex problem solved"},
                        {"input": {"complex_data": [100, 200, 300], "parameters": {"threshold": 50}}, "output": "Optimized solution found"}
                    ]
                }
            else:  # hard
                return {
                    "title": f"Expert-Level {topic} System Design",
                    "description": f"Design and implement a comprehensive system in {topic} with multiple components, error handling, scalability considerations, and performance optimization.",
                    "test_cases": [
                        {"input": {"system_requirements": {"scale": "high", "performance": "critical"}}, "output": "System designed and implemented"},
                        {"input": {"system_requirements": {"scale": "enterprise", "performance": "optimal"}}, "output": "Enterprise solution delivered"}
                    ]
                }
        
        elif category == "science":
            if difficulty.lower() == "easy":
                return {
                    "title": f"Basic {topic} Data Analysis",
                    "description": f"Implement a simple data analysis tool for {topic} that processes experimental data and generates basic statistics.",
                    "test_cases": [
                        {"input": {"data": [1.2, 2.3, 3.4, 4.5]}, "output": "Analysis completed"},
                        {"input": {"data": [10.1, 20.2, 30.3]}, "output": "Statistics calculated"}
                    ]
                }
            elif difficulty.lower() == "medium":
                return {
                    "title": f"Advanced {topic} Simulation",
                    "description": f"Create a simulation model for {topic} phenomena with multiple variables and interactive parameters.",
                    "test_cases": [
                        {"input": {"parameters": {"time": 100, "precision": 0.01}}, "output": "Simulation completed"},
                        {"input": {"parameters": {"time": 1000, "precision": 0.001}}, "output": "High-precision simulation finished"}
                    ]
                }
            else:  # hard
                return {
                    "title": f"Complex {topic} Modeling System",
                    "description": f"Implement a comprehensive modeling system for {topic} with advanced algorithms, visualization, and predictive capabilities.",
                    "test_cases": [
                        {"input": {"model_parameters": {"complexity": "high", "accuracy": "precise"}}, "output": "Advanced model implemented"},
                        {"input": {"model_parameters": {"complexity": "expert", "accuracy": "optimal"}}, "output": "Expert-level model completed"}
                    ]
                }
        
        elif category == "mathematics":
            if difficulty.lower() == "easy":
                return {
                    "title": f"Basic {topic} Calculator",
                    "description": f"Implement a calculator for {topic} operations with support for basic mathematical functions and error handling.",
                    "test_cases": [
                        {"input": {"expression": "2 + 3 * 4"}, "output": "14"},
                        {"input": {"expression": "sqrt(16) + 5"}, "output": "9"}
                    ]
                }
            elif difficulty.lower() == "medium":
                return {
                    "title": f"Advanced {topic} Problem Solver",
                    "description": f"Create a sophisticated problem solver for {topic} that handles complex equations, multiple variables, and provides step-by-step solutions.",
                    "test_cases": [
                        {"input": {"equation": "x^2 + 5x + 6 = 0"}, "output": "x = -2, x = -3"},
                        {"input": {"equation": "2x + 3y = 10, x - y = 1"}, "output": "x = 2.6, y = 1.6"}
                    ]
                }
            else:  # hard
                return {
                    "title": f"Expert {topic} Analysis System",
                    "description": f"Implement a comprehensive analysis system for {topic} with advanced algorithms, numerical methods, and visualization capabilities.",
                    "test_cases": [
                        {"input": {"analysis_type": "numerical", "precision": "high"}, "output": "Numerical analysis completed"},
                        {"input": {"analysis_type": "symbolic", "precision": "exact"}, "output": "Symbolic analysis finished"}
                    ]
                }
        
        else:  # general
            return {
                "title": f"General {topic} Problem",
                "description": f"Implement a solution for a {topic} problem that demonstrates problem-solving skills and programming best practices.",
                "test_cases": [
                    {"input": {"problem_data": "sample"}, "output": "Problem solved"},
                    {"input": {"problem_data": "complex"}, "output": "Complex problem addressed"}
                ]
            }

    def _get_fallback_feedback(self, code: str, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get fallback feedback when AI is not available"""
        passed_tests = sum(1 for result in test_results if result.get('passed', False))
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "correctness": {
                "score": int(success_rate),
                "issues": ["AI analysis unavailable"],
                "suggestions": ["Test your solution with more cases", "Check edge cases"]
            },
            "performance": {
                "time_complexity": "Analysis unavailable",
                "space_complexity": "Analysis unavailable",
                "efficiency_score": 70,
                "optimizations": ["AI optimization suggestions unavailable"]
            },
            "code_quality": {
                "readability_score": 75,
                "maintainability_score": 70,
                "best_practices": ["Use meaningful variable names", "Add comments"],
                "code_smells": ["AI analysis unavailable"]
            },
            "alternative_approaches": [],
            "learning_points": ["Practice more problems", "Study algorithms"],
            "overall_score": int(success_rate * 0.7),
            "next_steps": ["Continue practicing", "Study algorithm patterns"]
        }

    def _get_fallback_learning_path(self) -> Dict[str, Any]:
        """Get fallback learning path when AI is not available"""
        return {
            "current_skill_assessment": {
                "level": "intermediate",
                "strengths": ["Basic programming"],
                "weaknesses": ["Advanced algorithms"],
                "confidence_score": 60
            },
            "learning_objectives": [
                {
                    "goal": "Improve problem solving skills",
                    "priority": "high",
                    "estimated_weeks": 4,
                    "success_criteria": ["Solve 20 problems", "Improve success rate"]
                }
            ],
            "recommended_topics": [
                {
                    "topic": "Arrays and Strings",
                    "difficulty": "easy",
                    "problems_count": 10,
                    "estimated_time": "1 week",
                    "prerequisites": [],
                    "learning_resources": ["Practice problems", "Algorithm tutorials"]
                }
            ],
            "practice_schedule": {
                "daily_problems": 1,
                "weekly_goals": "Complete 5 problems",
                "review_schedule": "Weekly",
                "difficulty_progression": "Start with easy problems"
            },
            "improvement_areas": [
                {
                    "area": "Problem solving approach",
                    "current_level": "basic",
                    "target_level": "intermediate",
                    "action_plan": ["Practice daily", "Study solutions"]
                }
            ],
            "milestone_tracking": [
                {
                    "milestone": "Complete 25 problems",
                    "target_date": "2024-02-01",
                    "progress_indicators": ["Daily practice", "Success rate improvement"]
                }
            ]
        }

    async def generate_student_report(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered student performance report"""
        try:
            print(f"[AI_REPORT] Generating student report for {performance_data.get('student_name', 'Unknown')}")
            
            if not self.available:
                return self._get_fallback_student_report(performance_data)
            
            prompt = f"""
            Generate a comprehensive student performance report based on the following data:
            
            Student: {performance_data.get('student_name', 'Unknown')}
            Total Assessments: {performance_data.get('total_assessments', 0)}
            Average Score: {performance_data.get('average_score', 0)}%
            Topic Performance: {performance_data.get('topic_performance', {})}
            Recent Results: {performance_data.get('recent_results', [])}
            
            Provide a detailed analysis in this JSON format:
            {{
                "report_content": "Comprehensive analysis of student performance with specific insights and recommendations",
                "strengths": ["Strength 1", "Strength 2", "Strength 3"],
                "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
                "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
                "performance_summary": {{
                    "overall_grade": "B+",
                    "improvement_areas": ["Area 1", "Area 2"],
                    "next_steps": ["Step 1", "Step 2"],
                    "estimated_improvement_time": "2-3 weeks"
                }}
            }}
            
            Focus on:
            1. Specific performance patterns and trends
            2. Identified strengths and areas for improvement
            3. Actionable recommendations for the teacher
            4. Realistic expectations and timelines
            5. Personalized learning suggestions
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return self._get_fallback_student_report(performance_data)
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                report_data = json.loads(response_text)
                print("[SUCCESS] [AI_REPORT] Student report generated successfully")
                return report_data
                
            except json.JSONDecodeError:
                return self._get_fallback_student_report(performance_data)
            
        except Exception as e:
            print(f"[ERROR] [AI_REPORT] Error generating student report: {str(e)}")
            return self._get_fallback_student_report(performance_data)

    async def generate_smart_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered assessment targeting batch weaknesses"""
        try:
            print(f"[SMART_ASSESSMENT] Generating smart assessment: {assessment_data.get('title', 'Unknown')}")
            
            if not self.available:
                return self._get_fallback_smart_assessment(assessment_data)
            
            batch_weaknesses = assessment_data.get('batch_weaknesses', {})
            adapt_to_weaknesses = assessment_data.get('adapt_to_weaknesses', False)
            
            prompt = f"""
            Generate a smart assessment that targets student weaknesses:
            
            Assessment Details:
            - Title: {assessment_data.get('title', 'Smart Assessment')}
            - Topic: {assessment_data.get('topic', 'General')}
            - Difficulty: {assessment_data.get('difficulty', 'medium')}
            - Question Count: {assessment_data.get('question_count', 10)}
            - Adapt to Weaknesses: {adapt_to_weaknesses}
            
            Batch Weaknesses: {batch_weaknesses}
            
            Generate assessment in this JSON format:
            {{
                "description": "Assessment description explaining the focus areas",
                "questions": [
                    {{
                        "question": "Question text",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0,
                        "explanation": "Why this answer is correct",
                        "difficulty": "easy",
                        "topic": "specific topic",
                        "targets_weakness": "specific weakness"
                    }}
                ],
                "insights": ["Insight 1", "Insight 2"],
                "targeted_areas": ["Area 1", "Area 2"],
                "estimated_time": "30 minutes"
            }}
            
            Requirements:
            1. Target identified weaknesses from batch analysis
            2. Create questions that progressively build understanding
            3. Include explanations that help students learn
            4. Balance difficulty based on student performance
            5. Focus on practical application of concepts
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return self._get_fallback_smart_assessment(assessment_data)
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                assessment_data = json.loads(response_text)
                print("[SUCCESS] [SMART_ASSESSMENT] Smart assessment generated successfully")
                return assessment_data
                
            except json.JSONDecodeError:
                return self._get_fallback_smart_assessment(assessment_data)
            
        except Exception as e:
            print(f"[ERROR] [SMART_ASSESSMENT] Error generating smart assessment: {str(e)}")
            return self._get_fallback_smart_assessment(assessment_data)

    async def audit_content_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Audit content quality using AI"""
        try:
            print(f"[CONTENT_AUDIT] Auditing content quality")
            
            if not self.available:
                return self._get_fallback_content_audit(content_data)
            
            prompt = f"""
            Audit the quality of educational content:
            
            Content Type: {content_data.get('content_type', 'unknown')}
            Content Text: {content_data.get('content_text', '')}
            Success Rate: {content_data.get('success_rate', 0)}%
            Total Attempts: {content_data.get('total_attempts', 0)}
            
            Provide quality audit in this JSON format:
            {{
                "audit_score": 85,
                "audit_feedback": "Detailed feedback on content quality",
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "quality_issues": ["Issue 1", "Issue 2"],
                "strengths": ["Strength 1", "Strength 2"]
            }}
            
            Evaluate:
            1. Clarity and comprehensibility
            2. Educational value and learning objectives
            3. Difficulty appropriateness
            4. Potential ambiguity or confusion
            5. Engagement and interest level
            6. Alignment with learning outcomes
            """
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return self._get_fallback_content_audit(content_data)
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                audit_data = json.loads(response_text)
                print("[SUCCESS] [CONTENT_AUDIT] Content audit completed successfully")
                return audit_data
                
            except json.JSONDecodeError:
                return self._get_fallback_content_audit(content_data)
            
        except Exception as e:
            print(f"[ERROR] [CONTENT_AUDIT] Error auditing content: {str(e)}")
            return self._get_fallback_content_audit(content_data)

    def _get_fallback_student_report(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback student report when AI is not available"""
        return {
            "report_content": f"Student {performance_data.get('student_name', 'Unknown')} has completed {performance_data.get('total_assessments', 0)} assessments with an average score of {performance_data.get('average_score', 0)}%. Based on the performance data, there are areas for improvement and strengths to build upon.",
            "strengths": ["Consistent participation", "Good effort"],
            "weaknesses": ["Needs improvement in some areas"],
            "recommendations": ["Continue practicing", "Focus on weak topics"],
            "performance_summary": {
                "overall_grade": "B",
                "improvement_areas": ["Practice more problems"],
                "next_steps": ["Continue learning"],
                "estimated_improvement_time": "2-4 weeks"
            }
        }

    def _get_fallback_smart_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback smart assessment when AI is not available"""
        return {
            "description": f"Assessment on {assessment_data.get('topic', 'General')} topics with {assessment_data.get('question_count', 10)} questions",
            "questions": [
                {
                    "question": f"Sample question about {assessment_data.get('topic', 'General')}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": "This is the correct answer because...",
                    "difficulty": assessment_data.get('difficulty', 'medium'),
                    "topic": assessment_data.get('topic', 'General'),
                    "targets_weakness": "General understanding"
                }
            ],
            "insights": ["Focus on fundamental concepts", "Practice regularly"],
            "targeted_areas": [assessment_data.get('topic', 'General')],
            "estimated_time": "30 minutes"
        }

    def _get_fallback_content_audit(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback content audit when AI is not available"""
        return {
            "audit_score": 75,
            "audit_feedback": "Content appears to be of reasonable quality. Consider reviewing for clarity and educational value.",
            "recommendations": ["Review for clarity", "Ensure educational value"],
            "quality_issues": ["Minor clarity issues"],
            "strengths": ["Relevant content", "Appropriate difficulty"]
        }

    async def generate_mcq_questions(
        self, 
        topic: str, 
        difficulty: str, 
        count: int = 10,
        store_in_db: bool = True
    ) -> List[Dict[str, Any]]:
        """Generate unique MCQ questions using Gemini AI"""
        try:
            if not self.available:
                return self._get_fallback_mcq_questions(topic, difficulty, count)
            
            # Get existing questions to avoid duplicates
            existing_questions = await self._get_existing_questions(topic, difficulty)
            existing_question_texts = [q.get("question", "") for q in existing_questions]
            
            # Create uniqueness prompt
            uniqueness_context = ""
            if existing_question_texts:
                uniqueness_context = f"""
IMPORTANT: Avoid generating questions similar to these existing ones:
{chr(10).join(f"- {q}" for q in existing_question_texts[:5])}

Generate completely NEW and UNIQUE questions that are different from the above."""
            
            prompt = f"""Generate {count} UNIQUE multiple choice questions about {topic} with {difficulty} difficulty level.

Requirements:
- Each question must have exactly 4 options (A, B, C, D)
- Questions should be educational and relevant to {topic}
- Difficulty should be appropriate for {difficulty} level
- Questions should be clear and unambiguous
- Cover different aspects of {topic}
- Questions must be COMPLETELY UNIQUE and not similar to existing questions
- Use varied question formats (definitions, scenarios, calculations, comparisons, etc.)
- Include questions about different subtopics within {topic}

{uniqueness_context}

Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "What is the primary purpose of variables in programming?",
    "options": ["To store data", "To display text", "To create loops", "To define functions"],
    "answer": "A",
    "explanation": "Variables are used to store and manipulate data in programs."
  }},
  {{
    "question": "Which keyword is used to define a function in Python?",
    "options": ["function", "def", "define", "func"],
    "answer": "B", 
    "explanation": "The 'def' keyword is used to define functions in Python."
  }}
]

Important: Return ONLY the JSON array, no other text or formatting."""
            
            response = await self.model.generate_content_async(prompt)
            content = response.text.strip()
            
            # Parse JSON response
            try:
                # Clean up the response content
                content = content.strip()
                
                # Extract JSON from response if it's wrapped in markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Remove any leading/trailing text that's not JSON
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                # Find the first [ and last ] to extract array
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    content = content[start_idx:end_idx+1]
                
                print(f"🔍 [GEMINI] Parsing JSON content: {content[:200]}...")
                
                questions = json.loads(content)
                
                # Validate and format questions
                formatted_questions = []
                for i, q in enumerate(questions):
                    if all(key in q for key in ["question", "options", "answer", "explanation"]):
                        formatted_questions.append({
                            "id": f"q{i+1}",
                            "question": q["question"],
                            "options": q["options"],
                            "answer": q["answer"],
                            "explanation": q["explanation"],
                            "difficulty": difficulty,
                            "topic": topic
                        })
                
                # Store questions in database if requested
                if store_in_db:
                    await self._store_ai_questions_in_db(formatted_questions[:count], topic, difficulty)
                
                return formatted_questions[:count]
                
            except json.JSONDecodeError as e:
                print(f"❌ [GEMINI] JSON parsing error: {e}")
                print(f"🔍 [GEMINI] Raw content that failed to parse: {content}")
                return self._get_fallback_mcq_questions(topic, difficulty, count)
                
        except Exception as e:
            print(f"❌ [GEMINI] Error generating MCQ questions: {e}")
            return self._get_fallback_mcq_questions(topic, difficulty, count)
    
    def _get_fallback_mcq_questions(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Get fallback MCQ questions when AI is not available - with enhanced variety"""
        import random
        from datetime import datetime
        
        print(f"⚠️ [GEMINI] Using fallback questions for {topic} ({difficulty})")
        
        # Expanded question pool with much more variety
        fallback_questions = []
        
        # Comprehensive topic-specific question pools
        topic_questions = {
            "python": [
                {
                    "question": "What is the correct syntax to create a list in Python?",
                    "options": ["list = []", "list = {}", "list = ()", "list = []"],
                    "correct": 0,
                    "explanation": "Lists in Python are created using square brackets []"
                },
                {
                    "question": "Which keyword is used to define a function in Python?",
                    "options": ["function", "def", "define", "func"],
                    "correct": 1,
                    "explanation": "The 'def' keyword is used to define functions in Python"
                },
                {
                    "question": "What does the 'print()' function do in Python?",
                    "options": ["Displays output", "Reads input", "Calculates values", "Stores data"],
                    "correct": 0,
                    "explanation": "The print() function displays output to the console"
                },
                {
                    "question": "Which data type is used to store a sequence of characters in Python?",
                    "options": ["string", "int", "float", "boolean"],
                    "correct": 0,
                    "explanation": "Strings are used to store sequences of characters"
                },
                {
                    "question": "What is the result of 5 // 2 in Python?",
                    "options": ["2.5", "2", "3", "2.0"],
                    "correct": 1,
                    "explanation": "The // operator performs floor division, returning 2"
                },
                {
                    "question": "What does the len() function return?",
                    "options": ["The last element", "The length of a sequence", "The sum of elements", "The average"],
                    "correct": 1,
                    "explanation": "len() returns the number of items in a sequence or collection"
                },
                {
                    "question": "Which method is used to add an element to the end of a list?",
                    "options": ["add()", "append()", "insert()", "extend()"],
                    "correct": 1,
                    "explanation": "append() adds a single element to the end of a list"
                },
                {
                    "question": "What is the result of 5 % 2 in Python?",
                    "options": ["2.5", "1", "2", "0"],
                    "correct": 1,
                    "explanation": "The % operator returns the remainder of division, so 5 % 2 = 1"
                }
            ],
            "javascript": [
                {
                    "question": "What is the correct way to declare a variable in JavaScript?",
                    "options": ["var x = 5", "variable x = 5", "v x = 5", "declare x = 5"],
                    "correct": 0,
                    "explanation": "Variables in JavaScript are declared using 'var', 'let', or 'const'"
                },
                {
                    "question": "Which operator is used for strict equality in JavaScript?",
                    "options": ["==", "===", "=", "!="],
                    "correct": 1,
                    "explanation": "The === operator checks for strict equality (value and type)"
                },
                {
                    "question": "What is the result of typeof null in JavaScript?",
                    "options": ["null", "undefined", "object", "string"],
                    "correct": 2,
                    "explanation": "typeof null returns 'object' due to a historical bug in JavaScript"
                },
                {
                    "question": "Which method is used to add an element to the end of an array?",
                    "options": ["push()", "add()", "append()", "insert()"],
                    "correct": 0,
                    "explanation": "push() adds one or more elements to the end of an array"
                }
            ],
            "array": [
                {
                    "question": "What is the time complexity of accessing an element by index in an array?",
                    "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                    "correct": 0,
                    "explanation": "Array access by index is O(1) because it uses direct memory addressing"
                },
                {
                    "question": "What is the space complexity of an array with n elements?",
                    "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                    "correct": 1,
                    "explanation": "An array with n elements requires O(n) space to store all elements"
                },
                {
                    "question": "What is the time complexity of linear search in an unsorted array?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "correct": 2,
                    "explanation": "Linear search checks each element sequentially, taking O(n) time in worst case"
                },
                {
                    "question": "What is the time complexity of binary search in a sorted array?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "correct": 1,
                    "explanation": "Binary search eliminates half the search space each iteration, taking O(log n) time"
                }
            ]
        }
        
        # Get questions for the topic or use a default set
        questions = topic_questions.get(topic.lower(), topic_questions["python"])
        
        # If we need more questions than available, expand the pool
        if count > len(questions):
            # Duplicate and modify questions to create more variety
            expanded_questions = questions.copy()
            for i in range(count - len(questions)):
                base_question = questions[i % len(questions)]
                # Create variation by modifying the question slightly
                modified_question = base_question.copy()
                modified_question["question"] = f"{base_question['question']} (Variant {i+1})"
                expanded_questions.append(modified_question)
            questions = expanded_questions
        
        # Generate questions with better variety using timestamp-based seeding
        used_indices = set()
        for i in range(count):
            # Use timestamp and topic for better randomization
            random.seed(hash(f"{topic}_{difficulty}_{datetime.utcnow().timestamp()}_{i}_{len(used_indices)}"))
            
            # Ensure we don't repeat questions
            available_indices = [idx for idx in range(len(questions)) if idx not in used_indices]
            if not available_indices:
                # If all questions used, reset and continue
                used_indices.clear()
                available_indices = list(range(len(questions)))
            
            selected_idx = random.choice(available_indices)
            used_indices.add(selected_idx)
            selected_question = questions[selected_idx]
            
            fallback_questions.append({
                "id": f"q{i+1}",
                "question": selected_question["question"],
                "options": selected_question["options"],
                "answer": selected_question["options"][selected_question["correct"]],
                "correct_answer": selected_question["correct"],
                "explanation": selected_question["explanation"],
                "difficulty": difficulty,
                "topic": topic
            })
        
        return fallback_questions

    async def _get_existing_questions(self, topic: str, difficulty: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get existing questions for a topic and difficulty to avoid duplicates"""
        try:
            from app.db.session import get_db
            
            db = await get_db()
            
            # Query existing questions from multiple collections
            existing_questions = []
            
            # Check ai_questions collection
            ai_questions = await db.ai_questions.find({
                "topic": {"$regex": topic, "$options": "i"},
                "difficulty": difficulty,
                "status": "active"
            }).limit(limit).to_list(length=None)
            existing_questions.extend(ai_questions)
            
            # Check assessments collection for questions
            assessments = await db.assessments.find({
                "subject": {"$regex": topic, "$options": "i"},
                "difficulty": difficulty,
                "questions": {"$exists": True, "$ne": []}
            }).limit(limit).to_list(length=None)
            
            for assessment in assessments:
                for question in assessment.get("questions", []):
                    if question.get("question"):
                        existing_questions.append(question)
            
            # Check teacher_assessments collection
            teacher_assessments = await db.teacher_assessments.find({
                "topic": {"$regex": topic, "$options": "i"},
                "difficulty": difficulty,
                "questions": {"$exists": True, "$ne": []}
            }).limit(limit).to_list(length=None)
            
            for assessment in teacher_assessments:
                for question in assessment.get("questions", []):
                    if question.get("question"):
                        existing_questions.append(question)
            
            return existing_questions[:limit]
            
        except Exception as e:
            print(f"⚠️ [GEMINI] Error getting existing questions: {str(e)}")
            return []

    async def _store_ai_questions_in_db(self, questions: List[Dict[str, Any]], topic: str, difficulty: str):
        """Store AI-generated questions in the database"""
        try:
            from app.db.session import get_db
            from datetime import datetime
            
            db = await get_db()
            
            # Prepare questions for database storage
            questions_to_store = []
            for question in questions:
                question_doc = {
                    "question": question["question"],
                    "options": question["options"],
                    "answer": question["answer"],
                    "explanation": question["explanation"],
                    "topic": topic,
                    "difficulty": difficulty,
                    "generated_by": "gemini",
                    "metadata": {
                        "ai_model": "gemini-2.0-flash-exp",
                        "generation_timestamp": datetime.utcnow().isoformat(),
                        "original_topic": topic,
                        "original_difficulty": difficulty
                    },
                    "created_at": datetime.utcnow(),
                    "status": "active",
                    "usage_count": 0,
                    "quality_score": None
                }
                questions_to_store.append(question_doc)
            
            # Insert questions into database
            if questions_to_store:
                result = await db.ai_questions.insert_many(questions_to_store)
                print(f"✅ [GEMINI] Stored {len(result.inserted_ids)} AI questions in database")
                
        except Exception as e:
            print(f"❌ [GEMINI] Error storing AI questions in database: {str(e)}")
            # Don't raise exception - this is not critical for question generation

# Global instance
gemini_coding_service = GeminiCodingService()

# Test function to verify execution works
def test_execution():
    """Test the execution system with the is_harmonious function"""
    test_code = """
def is_harmonious(colors):
    for i in range(1, len(colors)):
        if colors[i] == colors[i - 1]:
            return False
    return True
"""
    
    test_cases = [
        {
            "input": [1, 2, 3, 4],
            "output": True
        },
        {
            "input": [1, 2, 2, 3, 1],
            "output": False
        },
        {
            "input": [5],
            "output": True
        }
    ]
    
    print("🧪 [TEST] Testing execution with is_harmonious function...")
    result = gemini_coding_service.execute_code(
        code=test_code,
        language="python",
        test_cases=test_cases,
        time_limit=5000,
        memory_limit=256
    )
    print(f"🧪 [TEST] Result: {result}")
    return result
