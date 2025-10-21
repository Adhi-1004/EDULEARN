"""
API Documentation Generator
Generates comprehensive API documentation for production
"""
import os
import json
from typing import Dict, List, Any
from pathlib import Path

class APIDocumentationGenerator:
    """Generates comprehensive API documentation"""
    
    def __init__(self, base_path: str = "docs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def generate_endpoint_docs(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate documentation for API endpoints"""
        docs = []
        
        for endpoint in endpoints:
            doc = f"""
## {endpoint['name']}

**Method:** `{endpoint['method']}`  
**Path:** `{endpoint['path']}`  
**Description:** {endpoint['description']}

### Parameters

{self._format_parameters(endpoint.get('parameters', []))}

### Request Body

{self._format_request_body(endpoint.get('request_body', {}))}

### Response

{self._format_response(endpoint.get('response', {}))}

### Example Request

```bash
curl -X {endpoint['method']} "https://api.edulearn.com{endpoint['path']}" \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(endpoint.get('example_request', {}), indent=2)}'
```

### Example Response

```json
{json.dumps(endpoint.get('example_response', {}), indent=2)}
```

### Error Responses

{self._format_error_responses(endpoint.get('error_responses', []))}

---
"""
            docs.append(doc)
        
        return "\n".join(docs)
    
    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """Format parameters documentation"""
        if not parameters:
            return "No parameters required."
        
        param_docs = []
        for param in parameters:
            param_docs.append(f"- **{param['name']}** ({param['type']}): {param['description']}")
        
        return "\n".join(param_docs)
    
    def _format_request_body(self, request_body: Dict[str, Any]) -> str:
        """Format request body documentation"""
        if not request_body:
            return "No request body required."
        
        return f"""
**Schema:** `{request_body.get('schema', 'N/A')}`

```json
{json.dumps(request_body.get('example', {}), indent=2)}
```
"""
    
    def _format_response(self, response: Dict[str, Any]) -> str:
        """Format response documentation"""
        if not response:
            return "No response body."
        
        return f"""
**Status:** `{response.get('status', 'N/A')}`  
**Schema:** `{response.get('schema', 'N/A')}`

```json
{json.dumps(response.get('example', {}), indent=2)}
```
"""
    
    def _format_error_responses(self, error_responses: List[Dict[str, Any]]) -> str:
        """Format error responses documentation"""
        if not error_responses:
            return "No specific error responses."
        
        error_docs = []
        for error in error_responses:
            error_docs.append(f"- **{error['status']}**: {error['description']}")
        
        return "\n".join(error_docs)
    
    def generate_complete_documentation(self) -> str:
        """Generate complete API documentation"""
        
        # Define all API endpoints
        endpoints = [
            {
                "name": "User Registration",
                "method": "POST",
                "path": "/api/auth/register",
                "description": "Register a new user account",
                "request_body": {
                    "schema": "UserCreate",
                    "example": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "password": "securePassword123",
                        "role": "student"
                    }
                },
                "response": {
                    "status": "201 Created",
                    "schema": "UserResponse",
                    "example": {
                        "id": "user_123",
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "role": "student",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                },
                "error_responses": [
                    {"status": "400", "description": "Invalid input data"},
                    {"status": "409", "description": "Email already exists"}
                ]
            },
            {
                "name": "User Login",
                "method": "POST",
                "path": "/api/auth/login",
                "description": "Authenticate user and get JWT token",
                "request_body": {
                    "schema": "UserLogin",
                    "example": {
                        "email": "john.doe@example.com",
                        "password": "securePassword123"
                    }
                },
                "response": {
                    "status": "200 OK",
                    "schema": "LoginResponse",
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": "user_123",
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "role": "student"
                        }
                    }
                },
                "error_responses": [
                    {"status": "401", "description": "Invalid credentials"},
                    {"status": "422", "description": "Validation error"}
                ]
            },
            {
                "name": "Create Assessment",
                "method": "POST",
                "path": "/api/assessments",
                "description": "Create a new assessment",
                "parameters": [
                    {"name": "Authorization", "type": "header", "description": "JWT token"}
                ],
                "request_body": {
                    "schema": "AssessmentCreate",
                    "example": {
                        "title": "Mathematics Assessment - Algebra Basics",
                        "description": "Comprehensive assessment covering basic algebraic concepts",
                        "subject": "Mathematics",
                        "difficulty": "intermediate",
                        "time_limit": 60,
                        "questions": [
                            {
                                "question": "What is the value of x in the equation 2x + 5 = 13?",
                                "options": ["3", "4", "5", "6"],
                                "correct_answer": 0,
                                "explanation": "Solving: 2x + 5 = 13, 2x = 8, x = 4"
                            }
                        ],
                        "max_attempts": 3,
                        "type": "mcq",
                        "batches": ["batch_1", "batch_2"]
                    }
                },
                "response": {
                    "status": "201 Created",
                    "schema": "AssessmentResponse",
                    "example": {
                        "id": "assessment_123",
                        "title": "Mathematics Assessment - Algebra Basics",
                        "description": "Comprehensive assessment covering basic algebraic concepts",
                        "subject": "Mathematics",
                        "difficulty": "intermediate",
                        "time_limit": 60,
                        "total_questions": 1,
                        "created_by": "teacher_456",
                        "created_at": "2024-01-01T00:00:00Z",
                        "is_active": True
                    }
                },
                "error_responses": [
                    {"status": "401", "description": "Unauthorized"},
                    {"status": "403", "description": "Insufficient permissions"},
                    {"status": "422", "description": "Validation error"}
                ]
            },
            {
                "name": "Get Assessment Questions",
                "method": "GET",
                "path": "/api/assessments/{assessment_id}/questions",
                "description": "Get questions for a specific assessment",
                "parameters": [
                    {"name": "assessment_id", "type": "path", "description": "Assessment ID"},
                    {"name": "Authorization", "type": "header", "description": "JWT token"}
                ],
                "response": {
                    "status": "200 OK",
                    "schema": "AssessmentQuestionsResponse",
                    "example": {
                        "assessment_id": "assessment_123",
                        "title": "Mathematics Assessment - Algebra Basics",
                        "questions": [
                            {
                                "id": "question_1",
                                "question": "What is the value of x in the equation 2x + 5 = 13?",
                                "options": ["3", "4", "5", "6"],
                                "type": "mcq"
                            }
                        ],
                        "time_limit": 60,
                        "total_questions": 1
                    }
                },
                "error_responses": [
                    {"status": "401", "description": "Unauthorized"},
                    {"status": "404", "description": "Assessment not found"},
                    {"status": "403", "description": "Access denied"}
                ]
            },
            {
                "name": "Submit Assessment",
                "method": "POST",
                "path": "/api/assessments/{assessment_id}/submit",
                "description": "Submit assessment answers",
                "parameters": [
                    {"name": "assessment_id", "type": "path", "description": "Assessment ID"},
                    {"name": "Authorization", "type": "header", "description": "JWT token"}
                ],
                "request_body": {
                    "schema": "AssessmentSubmission",
                    "example": {
                        "answers": [
                            {
                                "question_id": "question_1",
                                "answer": 1,
                                "time_taken": 30
                            }
                        ],
                        "total_time": 30
                    }
                },
                "response": {
                    "status": "200 OK",
                    "schema": "AssessmentResult",
                    "example": {
                        "assessment_id": "assessment_123",
                        "student_id": "student_456",
                        "score": 0,
                        "total_questions": 1,
                        "correct_answers": 0,
                        "incorrect_answers": 1,
                        "time_taken": 30,
                        "submitted_at": "2024-01-01T00:00:00Z",
                        "answers": [
                            {
                                "question_id": "question_1",
                                "answer": 1,
                                "correct_answer": 0,
                                "is_correct": False,
                                "time_taken": 30
                            }
                        ]
                    }
                },
                "error_responses": [
                    {"status": "401", "description": "Unauthorized"},
                    {"status": "404", "description": "Assessment not found"},
                    {"status": "422", "description": "Validation error"}
                ]
            }
        ]
        
        # Generate documentation sections
        sections = [
            "# EDULEARN API Documentation",
            "",
            "## Overview",
            "",
            "EDULEARN is a comprehensive educational assessment platform that provides APIs for creating, managing, and analyzing assessments.",
            "",
            "### Base URL",
            "```",
            "https://api.edulearn.com",
            "```",
            "",
            "### Authentication",
            "All protected endpoints require JWT authentication. Include the token in the Authorization header:",
            "```",
            "Authorization: Bearer <your-jwt-token>",
            "```",
            "",
            "## API Endpoints",
            "",
            self.generate_endpoint_docs(endpoints),
            "",
            "## Error Handling",
            "",
            "All API errors return structured JSON responses:",
            "",
            "```json",
            "{",
            '  "detail": "Error message",',
            '  "error_code": "ERROR_CODE",',
            '  "timestamp": "2024-01-01T00:00:00Z"',
            "}",
            "```",
            "",
            "### Common Error Codes",
            "",
            "| Code | HTTP Status | Description |",
            "|------|-------------|-------------|",
            "| `INVALID_CREDENTIALS` | 401 | Invalid email/password |",
            "| `TOKEN_EXPIRED` | 401 | JWT token has expired |",
            "| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |",
            "| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |",
            "| `VALIDATION_ERROR` | 422 | Request data validation failed |",
            "| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |",
            "",
            "## Rate Limiting",
            "",
            "API requests are rate-limited to ensure fair usage:",
            "",
            "| Category | Limit | Window |",
            "|----------|-------|--------|",
            "| General API | 100 requests | 1 minute |",
            "| Assessment Creation | 10 requests | 1 minute |",
            "| Code Execution | 20 requests | 1 minute |",
            "",
            "## SDKs and Libraries",
            "",
            "### JavaScript/TypeScript",
            "```bash",
            "npm install @edulearn/api-client",
            "```",
            "",
            "### Python",
            "```bash",
            "pip install edulearn-api",
            "```",
            "",
            "## Support",
            "",
            "For API support and questions:",
            "- Email: support@edulearn.com",
            "- Documentation: https://docs.edulearn.com",
            "- Status Page: https://status.edulearn.com"
        ]
        
        return "\n".join(sections)
    
    def save_documentation(self, content: str, filename: str = "API_DOCUMENTATION.md"):
        """Save documentation to file"""
        file_path = self.base_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Documentation saved to: {file_path}")

# Generate and save documentation
if __name__ == "__main__":
    generator = APIDocumentationGenerator()
    docs = generator.generate_complete_documentation()
    generator.save_documentation(docs)
