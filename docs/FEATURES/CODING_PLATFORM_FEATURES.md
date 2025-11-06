# 💻 Coding Practice Platform Features

## Table of Contents
1. [Overview](#overview)
2. [AI-Powered Problem Generation](#ai-powered-problem-generation)
3. [Code Execution System](#code-execution-system)
4. [Solution Submission & Evaluation](#solution-submission--evaluation)
5. [Coding Sessions](#coding-sessions)
6. [Personal Analytics](#personal-analytics)
7. [AI-Powered Learning Paths](#ai-powered-learning-paths)

---

## Overview

The Coding Practice Platform is an intelligent system for learning programming through hands-on problem-solving with AI assistance and automated evaluation.

### Key Features
- 🤖 **AI Problem Generation** - Google Gemini creates unique problems
- 💻 **Multi-Language Support** - Python, JavaScript, Java, C++, and more
- ⚡ **Real-Time Execution** - Judge0 API for code testing
- 📊 **Progress Tracking** - Comprehensive analytics
- 🎯 **Personalized Learning** - AI-powered recommendations
- ✅ **Automated Testing** - Visible and hidden test cases

### Technology Stack
- **AI**: Google Gemini AI for problem generation
- **Execution**: Judge0 API for sandboxed code execution
- **Frontend**: Monaco Editor for code editing
- **Backend**: FastAPI with async processing

---

## AI-Powered Problem Generation

### Feature Overview
Dynamically generates unique coding problems tailored to user skill level and preferences using Google Gemini AI.

### Problem Generation Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Student    │    │   Frontend   │    │   Backend    │    │  Gemini AI   │    │   Database   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │                   │
       │ 1. Request Problem│                   │                   │                   │
       │    - Topic        │                   │                   │                   │
       │    - Difficulty   │                   │                   │                   │
       ├──────────────────▶│                   │                   │                   │
       │                   │                   │                   │                   │
       │                   │ 2. POST /coding/  │                   │                   │
       │                   │    problems/generate                  │                   │
       │                   │    {topic, difficulty,                │                   │
       │                   │     skill_level}  │                   │                   │
       │                   ├──────────────────▶│                   │                   │
       │                   │                   │                   │                   │
       │                   │                   │ 3. Get User       │                   │
       │                   │                   │    Analytics      │                   │
       │                   │                   ├──────────────────────────────────────▶│
       │                   │                   │                   │                   │
       │                   │                   │ 4. User Stats     │                   │
       │                   │                   │◀──────────────────────────────────────┤
       │                   │                   │                   │                   │
       │                   │                   │ 5. Generate Problem                   │
       │                   │                   │    Request        │                   │
       │                   │                   ├──────────────────▶│                   │
       │                   │                   │                   │                   │
       │                   │                   │                   │ 6. AI Processing │
       │                   │                   │                   │    - Topic analysis│
       │                   │                   │                   │    - Difficulty  │
       │                   │                   │                   │      calibration │
       │                   │                   │                   │    - Test case   │
       │                   │                   │                   │      generation  │
       │                   │                   │                   ├──────┐           │
       │                   │                   │                   │      │           │
       │                   │                   │                   │◀─────┘           │
       │                   │                   │                   │                   │
       │                   │                   │ 7. Problem Data   │                   │
       │                   │                   │    {title, desc,  │                   │
       │                   │                   │     test_cases}   │                   │
       │                   │                   │◀──────────────────┤                   │
       │                   │                   │                   │                   │
       │                   │                   │ 8. Save Problem   │                   │
       │                   │                   ├──────────────────────────────────────▶│
       │                   │                   │                   │                   │
       │                   │ 9. Problem Response                   │                   │
       │                   │◀──────────────────┤                   │                   │
       │                   │                   │                   │                   │
       │ 10. Display       │                   │                   │                   │
       │     Problem       │                   │                   │                   │
       │◀──────────────────┤                   │                   │                   │
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
```

### Files Involved

**Frontend:**
- `frontend/src/pages/coding/ProblemGenerator.tsx` - Problem generation UI
- `frontend/src/pages/coding/ProblemSolver.tsx` - Code editor interface
- `frontend/src/api/codingService.ts`
  - Function: `generateProblem(request)`

**Backend:**
- `backend/app/api/coding.py`
  - Endpoint: `POST /api/coding/problems/generate`
- `backend/app/services/gemini_coding_service.py`
  - Class: `GeminiCodingService`
  - Function: `generate_coding_problem(topic, difficulty, skill_level)`

### Implementation

**1. Frontend Problem Request**
```typescript
// File: frontend/src/api/codingService.ts
export const generateProblem = async (request: ProblemGenerationRequest) => {
  const response = await api.post('/coding/problems/generate', request);
  return response.data;
};

// File: frontend/src/pages/coding/ProblemGenerator.tsx
const ProblemGenerator: React.FC = () => {
  const [config, setConfig] = useState({
    topic: 'Arrays',
    difficulty: 'medium',
    user_skill_level: 'intermediate',
    focus_areas: ['Arrays', 'Sorting'],
    avoid_topics: []
  });
  
  const handleGenerate = async () => {
    setLoading(true);
    try {
      const result = await codingService.generateProblem({
        ...config,
        timestamp: Date.now(),
        session_id: sessionStorage.getItem('coding_session_id')
      });
      
      setProblem(result.problem);
      navigate(`/coding/solve/${result.problem.id}`);
    } catch (error) {
      toast.error('Failed to generate problem');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="problem-generator">
      <h2>Generate Coding Problem</h2>
      
      <select
        value={config.topic}
        onChange={(e) => setConfig({...config, topic: e.target.value})}
      >
        <option value="Arrays">Arrays</option>
        <option value="Strings">Strings</option>
        <option value="Dynamic Programming">Dynamic Programming</option>
        <option value="Graphs">Graphs</option>
        <option value="Trees">Trees</option>
      </select>
      
      <select
        value={config.difficulty}
        onChange={(e) => setConfig({...config, difficulty: e.target.value})}
      >
        <option value="easy">Easy</option>
        <option value="medium">Medium</option>
        <option value="hard">Hard</option>
      </select>
      
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Problem'}
      </button>
    </div>
  );
};
```

**2. Backend Problem Generation**
```python
# File: backend/app/api/coding.py
@router.post("/problems/generate")
async def generate_problem(
    request: dict,
    user_id: str = Depends(get_current_user_id)
):
    """Generate a new coding problem using Gemini AI"""
    try:
        # Extract parameters
        topic = request.get('topic', 'Arrays')
        difficulty = request.get('difficulty', 'easy')
        user_skill_level = request.get('user_skill_level', 'intermediate')
        focus_areas = request.get('focus_areas', [topic])
        avoid_topics = request.get('avoid_topics', [])
        
        # Get user analytics for personalization
        db = await get_db()
        user_analytics = await db.coding_analytics.find_one({
            "user_id": ObjectId(user_id)
        })
        
        # Generate problem using Gemini AI
        problem_data = await gemini_coding_service.generate_coding_problem(
            topic=topic,
            difficulty=difficulty,
            user_skill_level=user_skill_level,
            focus_areas=focus_areas,
            avoid_topics=avoid_topics
        )
        
        # Create problem document
        problem_doc = {
            "title": problem_data["title"],
            "description": problem_data["description"],
            "topic": problem_data["topic"],
            "difficulty": problem_data["difficulty"],
            "constraints": problem_data["constraints"],
            "examples": problem_data["examples"],
            "test_cases": problem_data["test_cases"],
            "hidden_test_cases": problem_data["hidden_test_cases"],
            "expected_complexity": problem_data["expected_complexity"],
            "hints": problem_data["hints"],
            "created_by": "AI",
            "created_at": datetime.utcnow(),
            "tags": problem_data["tags"],
            "success_rate": 0.0
        }
        
        # Save to database
        result = await db.coding_problems.insert_one(problem_doc)
        
        return {
            "success": True,
            "problem": {
                "id": str(result.inserted_id),
                **problem_data,
                "test_cases": problem_data["test_cases"]  # Visible test cases only
                # hidden_test_cases are NOT returned
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to generate problem: {str(e)}")
```

**3. Gemini AI Service**
```python
# File: backend/app/services/gemini_coding_service.py
import google.generativeai as genai
import json

class GeminiCodingService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_coding_problem(
        self,
        topic: str,
        difficulty: str,
        user_skill_level: str = "intermediate",
        focus_areas: list = None,
        avoid_topics: list = None
    ) -> dict:
        """Generate a unique coding problem using Gemini AI"""
        
        prompt = f"""
        Generate a unique coding problem with the following specifications:
        
        Topic: {topic}
        Difficulty: {difficulty}
        User Skill Level: {user_skill_level}
        Focus Areas: {', '.join(focus_areas or [topic])}
        Avoid Topics: {', '.join(avoid_topics or [])}
        
        Requirements:
        1. Create a realistic, practical problem
        2. Include clear problem statement
        3. Provide 2-3 example test cases
        4. Create 5 visible test cases (easy to medium)
        5. Create 5 hidden test cases (edge cases, corner cases)
        6. Include time and space complexity expectations
        7. Add 2-3 helpful hints
        8. Use appropriate difficulty level
        
        Return response in this exact JSON format:
        {{
          "title": "Problem Title",
          "description": "Detailed problem description",
          "topic": "{topic}",
          "difficulty": "{difficulty}",
          "constraints": ["constraint1", "constraint2"],
          "examples": [
            {{
              "input": "example input",
              "output": "example output",
              "explanation": "why this output"
            }}
          ],
          "test_cases": [
            {{"input": "test input", "expected_output": "expected"}}
          ],
          "hidden_test_cases": [
            {{"input": "hidden input", "expected_output": "expected"}}
          ],
          "expected_complexity": {{
            "time": "O(n)",
            "space": "O(1)"
          }},
          "hints": ["hint1", "hint2"],
          "tags": ["tag1", "tag2"]
        }}
        
        Make the problem unique and educational. Ensure test cases cover all edge cases.
        """
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from markdown if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            problem_data = json.loads(response_text)
            
            return problem_data
            
        except Exception as e:
            print(f"Error generating problem: {str(e)}")
            raise Exception(f"Failed to generate problem: {str(e)}")

# Global instance
gemini_coding_service = GeminiCodingService()
```

### Generated Problem Example

```json
{
  "title": "Two Sum Problem",
  "description": "Given an array of integers and a target sum, return indices of the two numbers that add up to the target.",
  "topic": "Arrays",
  "difficulty": "easy",
  "constraints": [
    "2 <= nums.length <= 10^4",
    "-10^9 <= nums[i] <= 10^9",
    "Only one valid answer exists"
  ],
  "examples": [
    {
      "input": "[2,7,11,15], target = 9",
      "output": "[0, 1]",
      "explanation": "nums[0] + nums[1] = 2 + 7 = 9"
    }
  ],
  "test_cases": [
    {"input": "[2,7,11,15]\n9", "expected_output": "[0, 1]"},
    {"input": "[3,2,4]\n6", "expected_output": "[1, 2]"}
  ],
  "hidden_test_cases": [
    {"input": "[-1,-2,-3,-4,-5]\n-8", "expected_output": "[2, 4]"},
    {"input": "[0,4,3,0]\n0", "expected_output": "[0, 3]"}
  ],
  "expected_complexity": {
    "time": "O(n)",
    "space": "O(n)"
  },
  "hints": [
    "Try using a hash map to store seen numbers",
    "For each number, check if (target - number) exists"
  ],
  "tags": ["arrays", "hash-table", "easy"]
}
```

---

## Code Execution System

### Feature Overview
Real-time code execution using Judge0 API with support for multiple programming languages.

### Code Execution Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Student    │    │   Frontend   │    │   Backend    │    │  Judge0 API  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       │ 1. Write Code     │                   │                   │
       │    in Editor      │                   │                   │
       │                   │                   │                   │
       │ 2. Click "Run"    │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ 3. POST /coding/  │                   │
       │                   │    execute        │                   │
       │                   │    {code,         │                   │
       │                   │     language,     │                   │
       │                   │     test_cases}   │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 4. Create         │
       │                   │                   │    Submissions    │
       │                   │                   │    (one per test) │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │                   │ 5. Execute Code
       │                   │                   │                   │    in Sandbox
       │                   │                   │                   ├──────┐
       │                   │                   │                   │      │
       │                   │                   │                   │◀─────┘
       │                   │                   │                   │
       │                   │                   │ 6. Get Tokens     │
       │                   │                   │◀──────────────────┤
       │                   │                   │                   │
       │                   │                   │ 7. Poll for       │
       │                   │                   │    Results        │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 8. Execution      │
       │                   │                   │    Results        │
       │                   │                   │◀──────────────────┤
       │                   │                   │                   │
       │                   │                   │ 9. Compare        │
       │                   │                   │    with Expected  │
       │                   │                   ├──────┐            │
       │                   │                   │      │            │
       │                   │                   │◀─────┘            │
       │                   │                   │                   │
       │                   │ 10. Results       │                   │
       │                   │     {passed,      │                   │
       │                   │      failed,      │                   │
       │                   │      details}     │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 11. Display       │                   │                   │
       │     Results       │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
```

### Implementation

**1. Frontend Code Editor**
```typescript
// File: frontend/src/pages/coding/ProblemSolver.tsx
import MonacoEditor from '@monaco-editor/react';

const ProblemSolver: React.FC = () => {
  const { problemId } = useParams();
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [results, setResults] = useState(null);
  const [executing, setExecuting] = useState(false);
  
  const handleRunCode = async () => {
    setExecuting(true);
    
    try {
      const result = await codingService.executeCode({
        code,
        language,
        problem_id: problemId,
        test_cases: problem.test_cases
      });
      
      setResults(result);
      
      if (result.all_passed) {
        toast.success('All test cases passed!');
      } else {
        toast.error(`${result.failed_count} test case(s) failed`);
      }
    } catch (error) {
      toast.error('Code execution failed');
    } finally {
      setExecuting(false);
    }
  };
  
  return (
    <div className="problem-solver">
      <div className="problem-description">
        <h2>{problem.title}</h2>
        <p>{problem.description}</p>
        <div className="examples">
          {problem.examples.map((ex, i) => (
            <div key={i} className="example">
              <strong>Example {i + 1}:</strong>
              <pre>Input: {ex.input}</pre>
              <pre>Output: {ex.output}</pre>
              <p>{ex.explanation}</p>
            </div>
          ))}
        </div>
      </div>
      
      <div className="code-editor">
        <div className="editor-header">
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
          
          <button onClick={handleRunCode} disabled={executing}>
            {executing ? 'Running...' : 'Run Code'}
          </button>
          
          <button onClick={handleSubmit}>Submit Solution</button>
        </div>
        
        <MonacoEditor
          height="60vh"
          language={language}
          value={code}
          onChange={setCode}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false
          }}
        />
        
        {results && (
          <div className="execution-results">
            <h3>Test Results</h3>
            <div className="summary">
              <span className="passed">{results.passed_count} Passed</span>
              <span className="failed">{results.failed_count} Failed</span>
            </div>
            
            {results.test_results.map((result, i) => (
              <div key={i} className={`test-result ${result.passed ? 'passed' : 'failed'}`}>
                <h4>Test Case {i + 1}</h4>
                <div>Input: <code>{result.input}</code></div>
                <div>Expected: <code>{result.expected}</code></div>
                <div>Got: <code>{result.output}</code></div>
                {result.error && <div className="error">{result.error}</div>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

**2. Backend Code Execution**
```python
# File: backend/app/api/coding.py
@router.post("/execute")
async def execute_code(
    request: CodeExecutionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Execute code against test cases"""
    try:
        # Execute code using Judge0
        results = await judge0_execution_service.execute_code(
            code=request.code,
            language=request.language,
            test_cases=request.test_cases
        )
        
        # Process results
        passed_count = sum(1 for r in results if r["passed"])
        failed_count = len(results) - passed_count
        
        return {
            "success": True,
            "all_passed": failed_count == 0,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "test_results": results
        }
        
    except Exception as e:
        raise HTTPException(500, f"Execution failed: {str(e)}")
```

**3. Judge0 Service**
```python
# File: backend/app/services/judge0_execution_service.py
import aiohttp
import asyncio
import base64

class Judge0ExecutionService:
    def __init__(self):
        self.api_url = JUDGE0_API_URL
        self.api_key = JUDGE0_API_KEY
        
        self.language_ids = {
            "python": 71,
            "javascript": 63,
            "java": 62,
            "cpp": 54,
            "c": 50
        }
    
    async def execute_code(
        self,
        code: str,
        language: str,
        test_cases: list
    ) -> list:
        """Execute code against multiple test cases"""
        language_id = self.language_ids.get(language, 71)
        
        results = []
        
        for test_case in test_cases:
            result = await self._execute_single(
                code,
                language_id,
                test_case["input"],
                test_case["expected_output"]
            )
            results.append(result)
        
        return results
    
    async def _execute_single(
        self,
        code: str,
        language_id: int,
        stdin: str,
        expected_output: str
    ) -> dict:
        """Execute code for a single test case"""
        
        async with aiohttp.ClientSession() as session:
            # Create submission
            submission_data = {
                "source_code": base64.b64encode(code.encode()).decode(),
                "language_id": language_id,
                "stdin": base64.b64encode(stdin.encode()).decode(),
                "expected_output": base64.b64encode(expected_output.encode()).decode()
            }
            
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Submit code
            async with session.post(
                f"{self.api_url}/submissions",
                json=submission_data,
                headers=headers,
                params={"base64_encoded": "true", "wait": "false"}
            ) as response:
                data = await response.json()
                token = data["token"]
            
            # Poll for result
            for _ in range(10):  # Max 10 attempts
                await asyncio.sleep(0.5)
                
                async with session.get(
                    f"{self.api_url}/submissions/{token}",
                    headers=headers,
                    params={"base64_encoded": "true"}
                ) as response:
                    result = await response.json()
                    
                    if result["status"]["id"] > 2:  # Not in queue or processing
                        break
            
            # Process result
            passed = result["status"]["id"] == 3  # Accepted
            
            output = ""
            if result.get("stdout"):
                output = base64.b64decode(result["stdout"]).decode()
            
            error = ""
            if result.get("stderr"):
                error = base64.b64decode(result["stderr"]).decode()
            elif result.get("compile_output"):
                error = base64.b64decode(result["compile_output"]).decode()
            
            return {
                "passed": passed,
                "input": stdin,
                "expected": expected_output,
                "output": output.strip(),
                "error": error,
                "time": result.get("time"),
                "memory": result.get("memory")
            }

# Global instance
judge0_execution_service = Judge0ExecutionService()
```

---

## Solution Submission & Evaluation

### Submit Solution Flow

```python
@router.post("/submit")
async def submit_solution(
    submission: CodingSolutionSubmit,
    user_id: str = Depends(get_current_user_id)
):
    """Submit solution for evaluation"""
    db = await get_db()
    
    # Get problem with hidden test cases
    problem = await db.coding_problems.find_one({
        "_id": ObjectId(submission.problem_id)
    })
    
    if not problem:
        raise HTTPException(404, "Problem not found")
    
    # Run all test cases (visible + hidden)
    all_test_cases = problem["test_cases"] + problem["hidden_test_cases"]
    
    results = await judge0_execution_service.execute_code(
        code=submission.code,
        language=submission.language,
        test_cases=all_test_cases
    )
    
    # Calculate score
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    score = (passed_count / total_count) * 100
    
    # Create submission document
    submission_doc = {
        "_id": str(uuid4()),
        "user_id": ObjectId(user_id),
        "problem_id": ObjectId(submission.problem_id),
        "code": submission.code,
        "language": submission.language,
        "score": score,
        "passed_count": passed_count,
        "total_count": total_count,
        "test_results": results,
        "submitted_at": datetime.utcnow(),
        "status": "accepted" if passed_count == total_count else "wrong_answer"
    }
    
    await db.coding_solutions.insert_one(submission_doc)
    
    # Update user analytics
    await update_coding_analytics(db, user_id, problem, passed_count == total_count)
    
    # Award XP
    xp_earned = calculate_coding_xp(problem["difficulty"], score)
    await award_xp(db, user_id, xp_earned)
    
    return {
        "submission_id": submission_doc["_id"],
        "score": score,
        "passed_count": passed_count,
        "total_count": total_count,
        "status": submission_doc["status"],
        "xp_earned": xp_earned
    }
```

---

## Coding Sessions

Track continuous coding practice sessions with time tracking and problem-solving progress.

```python
@router.post("/sessions/start")
async def start_session(
    session_data: CodingSessionStart,
    user_id: str = Depends(get_current_user_id)
):
    """Start a new coding session"""
    db = await get_db()
    
    session_doc = {
        "_id": str(uuid4()),
        "user_id": ObjectId(user_id),
        "problem_id": ObjectId(session_data.problem_id),
        "started_at": datetime.utcnow(),
        "ended_at": None,
        "duration": 0,
        "code_snapshots": [],
        "test_runs": 0,
        "status": "active"
    }
    
    await db.coding_sessions.insert_one(session_doc)
    
    return {"session_id": session_doc["_id"]}

@router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    update_data: CodingSessionUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """Update coding session with progress"""
    db = await get_db()
    
    update_dict = {}
    
    if update_data.code:
        update_dict["$push"] = {
            "code_snapshots": {
                "code": update_data.code,
                "timestamp": datetime.utcnow()
            }
        }
    
    if update_data.test_run:
        update_dict["$inc"] = {"test_runs": 1}
    
    await db.coding_sessions.update_one(
        {"_id": session_id, "user_id": ObjectId(user_id)},
        update_dict
    )
    
    return {"message": "Session updated"}

@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    final_status: str,
    user_id: str = Depends(get_current_user_id)
):
    """End coding session"""
    db = await get_db()
    
    session = await db.coding_sessions.find_one({
        "_id": session_id,
        "user_id": ObjectId(user_id)
    })
    
    if not session:
        raise HTTPException(404, "Session not found")
    
    duration = (datetime.utcnow() - session["started_at"]).total_seconds()
    
    await db.coding_sessions.update_one(
        {"_id": session_id},
        {
            "$set": {
                "ended_at": datetime.utcnow(),
                "duration": duration,
                "status": final_status
            }
        }
    )
    
    return {"message": "Session ended", "duration": duration}
```

---

## Personal Analytics

Comprehensive coding analytics dashboard tracking progress, strengths, and areas for improvement.

```python
@router.get("/analytics")
async def get_analytics(
    user_id: str = Depends(get_current_user_id)
):
    """Get personal coding analytics"""
    db = await get_db()
    
    # Get all submissions
    submissions = await db.coding_solutions.find({
        "user_id": ObjectId(user_id)
    }).to_list(length=None)
    
    # Calculate statistics
    total_problems = len(set(s["problem_id"] for s in submissions))
    total_submissions = len(submissions)
    accepted = len([s for s in submissions if s["status"] == "accepted"])
    
    # Topic-wise performance
    topic_stats = {}
    for submission in submissions:
        problem = await db.coding_problems.find_one({
            "_id": submission["problem_id"]
        })
        
        if problem:
            topic = problem["topic"]
            if topic not in topic_stats:
                topic_stats[topic] = {"attempted": 0, "solved": 0}
            
            topic_stats[topic]["attempted"] += 1
            if submission["status"] == "accepted":
                topic_stats[topic]["solved"] += 1
    
    # Difficulty-wise performance
    difficulty_stats = {
        "easy": {"attempted": 0, "solved": 0},
        "medium": {"attempted": 0, "solved": 0},
        "hard": {"attempted": 0, "solved": 0}
    }
    
    for submission in submissions:
        problem = await db.coding_problems.find_one({
            "_id": submission["problem_id"]
        })
        
        if problem:
            difficulty = problem["difficulty"]
            difficulty_stats[difficulty]["attempted"] += 1
            if submission["status"] == "accepted":
                difficulty_stats[difficulty]["solved"] += 1
    
    # Recent activity
    recent = sorted(submissions, key=lambda x: x["submitted_at"], reverse=True)[:10]
    
    return {
        "overview": {
            "total_problems_attempted": total_problems,
            "total_submissions": total_submissions,
            "problems_solved": accepted,
            "acceptance_rate": (accepted / total_submissions * 100) if submissions else 0
        },
        "topic_performance": topic_stats,
        "difficulty_performance": difficulty_stats,
        "recent_activity": recent
    }
```

---

## AI-Powered Learning Paths

Generate personalized learning paths based on user performance.

```python
@router.post("/analytics/learning-path")
async def generate_learning_path(
    user_id: str = Depends(get_current_user_id)
):
    """Generate AI-powered learning path"""
    db = await get_db()
    
    # Get user analytics
    analytics = await get_analytics(user_id)
    
    # Identify weak areas
    weak_topics = []
    for topic, stats in analytics["topic_performance"].items():
        if stats["attempted"] > 0:
            success_rate = stats["solved"] / stats["attempted"]
            if success_rate < 0.5:
                weak_topics.append(topic)
    
    # Generate learning path using Gemini
    prompt = f"""
    Generate a personalized coding learning path for a student with this performance:
    
    Topics Mastered: {[t for t, s in analytics["topic_performance"].items() if s["solved"] / s["attempted"] > 0.7]}
    Topics Need Practice: {weak_topics}
    Overall Acceptance Rate: {analytics["overview"]["acceptance_rate"]:.1f}%
    
    Provide:
    1. Recommended study order (topics)
    2. Specific problem types to focus on
    3. Practice strategy
    4. Time estimates
    
    Format as JSON with: {{ "path": [...], "recommendations": [...] }}
    """
    
    response = gemini_coding_service.model.generate_content(prompt)
    learning_path = json.loads(response.text)
    
    return learning_path
```

---

## Summary

### Coding Platform Architecture

```
Student → Request Problem → Gemini AI Generates → Save to DB
                              ↓
Student → Write Code → Execute via Judge0 → Compare Results
                              ↓
Student → Submit Solution → Test All Cases → Calculate Score → Update Analytics
                              ↓
                        Award XP/Badges → Generate Learning Path
```

### Key Database Collections

1. **coding_problems** - Generated problems with test cases
2. **coding_solutions** - User submissions and scores
3. **coding_sessions** - Practice session tracking
4. **coding_analytics** - User performance data

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/coding/problems/generate` | POST | Generate new problem |
| `/coding/problems` | GET | List problems |
| `/coding/execute` | POST | Run code (visible tests) |
| `/coding/submit` | POST | Submit solution (all tests) |
| `/coding/sessions/start` | POST | Start practice session |
| `/coding/sessions/{id}` | PUT | Update session |
| `/coding/analytics` | GET | Get personal analytics |
| `/coding/analytics/learning-path` | POST | Generate learning path |

---

**[Back to Features Overview](./FEATURES_OVERVIEW.md)**


