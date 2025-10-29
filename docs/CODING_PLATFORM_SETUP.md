# 🚀 Coding Platform Setup Guide

This guide will help you set up the AI-powered coding platform with real code execution using Judge0 API.

## Overview

The coding platform now features:
- ✅ **Real Code Execution** via Judge0 API (not simulated!)
- ✅ **Monaco Editor** - Professional code editor with syntax highlighting, autocomplete, and IntelliSense
- ✅ **Multi-Language Support** - Python, JavaScript, Java, C++
- ✅ **Test Case Validation** - Run code against multiple test cases with detailed feedback
- ✅ **Expandable Test Results** - Click to see detailed input/output comparison
- ✅ **AI-Generated Problems** - Unique coding problems powered by Google Gemini
- ✅ **Hints System** - Progressive hints to help students solve problems
- ✅ **Session Tracking** - Track keystrokes, time spent, and hints used

## 🔧 Setup Instructions

### Step 1: Get Judge0 API Key

The platform uses Judge0 CE (Community Edition) for secure code execution.

1. **Get RapidAPI Account**:
   - Go to [RapidAPI Judge0 CE](https://rapidapi.com/judge0-official/api/judge0-ce)
   - Sign up or log in to RapidAPI
   - Subscribe to Judge0 CE API (Free tier available with 50 requests/day)

2. **Copy Your API Key**:
   - After subscribing, copy your `X-RapidAPI-Key` from the API dashboard

### Step 2: Configure Backend Environment

1. **Update `.env` file** in the `backend` directory:

```env
# Judge0 API Configuration
JUDGE0_API_KEY=your-rapidapi-key-here
JUDGE0_API_HOST=judge0-ce.p.rapidapi.com
```

2. **Verify Configuration**:
   - Make sure MongoDB is running
   - Make sure Gemini API key is configured
   - Restart the backend server

### Step 3: Test the Platform

1. **Start Backend**:
```bash
cd backend
python start_server.py
```

2. **Start Frontend**:
```bash
cd frontend
npm run dev
```

3. **Test Flow**:
   - Login as a student
   - Go to "Assessment Choice" → "Coding Challenge"
   - Generate a new coding problem
   - Write code in the Monaco editor
   - Click "Run Code" to test against test cases
   - Click "Submit" when all tests pass

## 🎯 Features Explained

### 1. AI-Generated Coding Problems

Problems are generated using Google Gemini AI with:
- **Unique Problems**: Each generation creates a different problem
- **Adaptive Difficulty**: Easy, Medium, Hard levels
- **Topic-Based**: Arrays, Strings, Dynamic Programming, etc.
- **Comprehensive Details**: Description, examples, constraints, hints, test cases

### 2. Monaco Code Editor

Professional code editor with:
- **Syntax Highlighting**: Real-time syntax coloring
- **IntelliSense**: Smart autocomplete suggestions
- **Error Detection**: Syntax error highlighting
- **Multi-Language**: Supports Python, JavaScript, Java, C++
- **Code Folding**: Collapse/expand code blocks
- **Bracket Matching**: Highlight matching brackets

### 3. Code Execution Flow

```
Student Writes Code → Click "Run" → Judge0 API → Test Against Cases → Show Results
```

**Execution Process**:
1. Student writes code in Monaco editor
2. Code is sent to backend `/api/coding/execute` endpoint
3. Backend forwards to Judge0 API with test cases
4. Judge0 executes code in isolated container
5. Results are compared against expected outputs
6. Detailed feedback is shown to student

### 4. Test Results Display

**Expandable Test Cases**:
- Click test case to expand/collapse details
- See input, expected output, actual output
- View execution time and memory usage
- Error messages for failed tests
- Detailed comparison of outputs

### 5. Submission Flow

```
Run Tests → Validate All Pass → Submit → Save to Database → Award XP
```

**Submission Requirements**:
- All test cases must pass before submission
- Code is validated against visible test cases
- Backend saves code, results, and analytics
- XP is awarded based on difficulty

## 📊 API Endpoints

### Coding Platform Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/coding/problems/generate` | POST | Generate new AI problem |
| `/api/coding/problems` | GET | List all problems |
| `/api/coding/problems/{id}` | GET | Get specific problem |
| `/api/coding/execute` | POST | Execute code with test cases |
| `/api/coding/submit` | POST | Submit solution |
| `/api/coding/analytics` | GET | Get user coding analytics |
| `/api/coding/sessions/start` | POST | Start coding session |

### Execute Code Request

```json
{
  "code": "def solution(nums):\n    return sum(nums)",
  "language": "python",
  "test_cases": [
    {
      "input": [1, 2, 3],
      "output": 6
    },
    {
      "input": [10, 20],
      "output": 30
    }
  ],
  "timeout": 10
}
```

### Execute Code Response

```json
{
  "success": true,
  "execution_result": {
    "success": true,
    "execution_time": 125,
    "memory_used": 4096,
    "results": [
      {
        "passed": true,
        "input": [1, 2, 3],
        "expected": 6,
        "output": "6",
        "execution_time": 62.5,
        "memory": 2048,
        "error": null
      },
      {
        "passed": true,
        "input": [10, 20],
        "expected": 30,
        "output": "30",
        "execution_time": 62.5,
        "memory": 2048,
        "error": null
      }
    ]
  }
}
```

## 🐛 Troubleshooting

### Problem: Code execution fails

**Solution**:
1. Check Judge0 API key in `.env`
2. Verify RapidAPI subscription is active
3. Check request limits (50/day on free tier)
4. Check backend logs for detailed errors

### Problem: "No result received from Judge0"

**Solution**:
1. Judge0 API might be slow - increase timeout
2. Check network connectivity
3. Verify API key is correct
4. Check RapidAPI dashboard for errors

### Problem: Test cases always fail

**Solution**:
1. Verify test case format (input/output)
2. Check code syntax errors
3. Ensure function signature matches expected
4. Check stdout vs return value (Python uses runner)

### Problem: Monaco editor not loading

**Solution**:
1. Check console for errors
2. Ensure `@monaco-editor/react` is installed
3. Clear browser cache
4. Check network tab for CDN issues

## 🎨 Customization

### Add New Language Support

1. **Update Language Map** in `judge0_execution_service.py`:

```python
LANGUAGE_ID_MAP = {
    "python": 71,
    "javascript": 63,
    "java": 62,
    "cpp": 54,
    "ruby": 72,  # Add new language
}
```

2. **Add Language Template** in `CodingTestInterface.tsx`:

```typescript
const languages = [
  // ... existing languages
  {
    value: "ruby",
    label: "Ruby",
    template: "# Write your solution here\ndef solution\n  # Your code\nend"
  },
]
```

### Customize Test Case Display

Edit `CodingTestInterface.tsx` in the test results section to modify colors, layout, or information shown.

### Adjust Execution Timeout

In API call:
```typescript
const response = await api.post("/api/coding/execute", {
  code,
  language,
  test_cases: testCases,
  timeout: 20, // Increase timeout to 20 seconds
})
```

## 📈 Analytics & Tracking

The platform tracks:
- **Problems Solved**: Total accepted solutions
- **Success Rate**: Percentage of passing submissions
- **Coding Streak**: Consecutive days of solving
- **Preferred Language**: Most used programming language
- **Average Time**: Time per problem
- **Skill Level**: Beginner, Intermediate, Advanced
- **Strong/Weak Topics**: Based on performance

## 🔒 Security

### Judge0 Security

- Code executes in **isolated containers**
- **Resource limits**: CPU time, memory, output size
- **Network isolation**: No internet access during execution
- **Sandboxed environment**: No file system access

### Backend Security

- **Authentication required**: JWT tokens for all requests
- **Input validation**: Sanitize code and test cases
- **Rate limiting**: Prevent API abuse
- **Error handling**: Don't expose sensitive info

## 🎓 Student Experience

### Problem Solving Flow

1. **Select Topic & Difficulty**: Choose from 20+ topics
2. **Generate Problem**: AI creates unique problem
3. **Read Description**: Understand requirements
4. **View Examples**: See sample inputs/outputs
5. **Write Code**: Use Monaco editor
6. **Run Tests**: Validate against test cases
7. **Debug**: Use hints if stuck
8. **Submit**: Get XP and feedback

### Hints System

- **Progressive Disclosure**: Unlock hints one at a time
- **Penalty-Free**: No XP deduction for using hints
- **Contextual**: Hints specific to problem
- **Limited**: Usually 3-5 hints per problem

## 🚀 Performance Tips

1. **Use Judge0 Batch API**: For multiple test cases
2. **Cache Problem Templates**: Reduce DB queries
3. **Lazy Load Monaco**: Load editor only when needed
4. **Optimize Test Cases**: Keep them small and focused
5. **Index Database**: Add indexes to problem queries

## 📝 Example Problems

### Easy: Two Sum
```python
def solution(nums, target):
    # Find two numbers that add up to target
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
```

### Medium: Reverse Linked List
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def solution(head):
    prev = None
    current = head
    while current:
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node
    return prev
```

## 🔗 Resources

- [Judge0 Documentation](https://ce.judge0.com/)
- [RapidAPI Judge0](https://rapidapi.com/judge0-official/api/judge0-ce)
- [Monaco Editor Docs](https://microsoft.github.io/monaco-editor/)
- [Google Gemini AI](https://ai.google.dev/)

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Review backend logs
3. Check browser console
4. Verify API keys and configuration
5. Contact support with error details

---

**Happy Coding! 🎉**

