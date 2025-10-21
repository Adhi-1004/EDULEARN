"""
OpenAPI Configuration
Production-ready API documentation configuration
"""
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from typing import Dict, Any

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Generate custom OpenAPI schema for production"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="EDULEARN API",
        version="1.0.0",
        description="""
        ## EDULEARN - Educational Assessment Platform API
        
        A comprehensive educational platform for creating, managing, and analyzing assessments.
        
        ### Features
        - **User Management**: Student, teacher, and admin role management
        - **Assessment Creation**: AI-powered and manual assessment creation
        - **Batch Management**: Organize students into batches for targeted assessments
        - **Real-time Analytics**: Performance tracking and insights
        - **Coding Platform**: Interactive coding challenges and execution
        - **Notification System**: Real-time updates and alerts
        
        ### Authentication
        All endpoints require JWT authentication except for login/register.
        Include the JWT token in the Authorization header: `Bearer <token>`
        
        ### Rate Limiting
        - General API: 100 requests per minute per user
        - Assessment creation: 10 requests per minute per user
        - Code execution: 20 requests per minute per user
        
        ### Error Handling
        All errors return structured JSON responses with appropriate HTTP status codes.
        """,
        routes=app.routes,
    )
    
    # Add custom tags for better organization
    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "User authentication and authorization"
        },
        {
            "name": "Users",
            "description": "User management and profile operations"
        },
        {
            "name": "Assessments",
            "description": "Assessment creation, management, and submission"
        },
        {
            "name": "Teacher",
            "description": "Teacher-specific operations and analytics"
        },
        {
            "name": "Admin",
            "description": "Administrative operations and system management"
        },
        {
            "name": "Coding",
            "description": "Coding problems and execution platform"
        },
        {
            "name": "Notifications",
            "description": "Notification management and delivery"
        },
        {
            "name": "Health",
            "description": "System health monitoring and status checks"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for authentication"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add server information
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.edulearn.com",
            "description": "Production server"
        }
    ]
    
    # Add contact and license information
    openapi_schema["info"]["contact"] = {
        "name": "EDULEARN Support",
        "email": "support@edulearn.com",
        "url": "https://edulearn.com/support"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def add_examples_to_schemas(openapi_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Add examples to API schemas for better documentation"""
    
    # Assessment creation example
    if "AssessmentCreate" in openapi_schema.get("components", {}).get("schemas", {}):
        openapi_schema["components"]["schemas"]["AssessmentCreate"]["example"] = {
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
    
    # User registration example
    if "UserCreate" in openapi_schema.get("components", {}).get("schemas", {}):
        openapi_schema["components"]["schemas"]["UserCreate"]["example"] = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "securePassword123",
            "role": "student"
        }
    
    # Batch creation example
    if "BatchCreate" in openapi_schema.get("components", {}).get("schemas", {}):
        openapi_schema["components"]["schemas"]["BatchCreate"]["example"] = {
            "name": "Grade 10 Mathematics",
            "description": "Advanced mathematics batch for grade 10 students",
            "subject": "Mathematics",
            "grade_level": "10"
        }
    
    return openapi_schema
