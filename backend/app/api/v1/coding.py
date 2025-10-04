"""
Coding platform endpoints
Handles coding challenges, code execution, and programming assessments
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ...core.security import security_manager
from ...db import get_db
from ...models.models import UserModel
from ...dependencies import require_student_or_above, require_teacher_or_admin
from ...services.code_execution_service import CodeExecutionService
from ...services.gemini_coding_service import GeminiCodingService

router = APIRouter()

# Request/Response Models
class CodingProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")
    language: str = Field(..., regex="^(python|javascript|java|cpp)$")
    test_cases: List[Dict[str, Any]]
    starter_code: str
    hints: Optional[List[str]] = None

class CodingProblemResponse(BaseModel):
    problem_id: str
    title: str
    description: str
    difficulty: str
    language: str
    test_cases: List[Dict[str, Any]]
    starter_code: str
    hints: Optional[List[str]] = None
    created_at: datetime
    is_active: bool

class CodeSubmission(BaseModel):
    problem_id: str
    code: str
    language: str

class CodeExecutionResult(BaseModel):
    submission_id: str
    problem_id: str
    student_id: str
    code: str
    language: str
    test_results: List[Dict[str, Any]]
    passed_tests: int
    total_tests: int
    execution_time: float
    memory_usage: float
    status: str
    submitted_at: datetime

class CodingStatsResponse(BaseModel):
    total_problems: int
    problems_solved: int
    average_score: float
    favorite_language: str
    difficulty_distribution: Dict[str, int]

# Initialize services
code_execution_service = CodeExecutionService()
gemini_service = GeminiCodingService()

@router.get("/problems", response_model=List[CodingProblemResponse])
async def get_coding_problems(
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    language: Optional[str] = Query(None, regex="^(python|javascript|java|cpp)$"),
    current_user: UserModel = Depends(require_student_or_above)
):
    """Get list of coding problems"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {"is_active": True}
        if difficulty:
            filter_dict["difficulty"] = difficulty
        if language:
            filter_dict["language"] = language
        
        # Get problems
        problems_cursor = db.coding_problems.find(filter_dict).sort("created_at", -1)
        problems = []
        
        async for problem_doc in problems_cursor:
            problems.append(CodingProblemResponse(
                problem_id=str(problem_doc["_id"]),
                title=problem_doc["title"],
                description=problem_doc["description"],
                difficulty=problem_doc["difficulty"],
                language=problem_doc["language"],
                test_cases=problem_doc["test_cases"],
                starter_code=problem_doc["starter_code"],
                hints=problem_doc.get("hints"),
                created_at=problem_doc["created_at"],
                is_active=problem_doc["is_active"]
            ))
        
        return problems
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coding problems: {str(e)}"
        )

@router.get("/problems/{problem_id}", response_model=CodingProblemResponse)
async def get_coding_problem(
    problem_id: str,
    current_user: UserModel = Depends(require_student_or_above)
):
    """Get specific coding problem by ID"""
    try:
        db = await get_db()
        
        problem_doc = await db.coding_problems.find_one({"_id": problem_id})
        if not problem_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coding problem not found"
            )
        
        return CodingProblemResponse(
            problem_id=str(problem_doc["_id"]),
            title=problem_doc["title"],
            description=problem_doc["description"],
            difficulty=problem_doc["difficulty"],
            language=problem_doc["language"],
            test_cases=problem_doc["test_cases"],
            starter_code=problem_doc["starter_code"],
            hints=problem_doc.get("hints"),
            created_at=problem_doc["created_at"],
            is_active=problem_doc["is_active"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coding problem: {str(e)}"
        )

@router.post("/problems", response_model=CodingProblemResponse)
async def create_coding_problem(
    problem: CodingProblemCreate,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Create a new coding problem (Teacher/Admin only)"""
    try:
        db = await get_db()
        
        # Create problem document
        problem_doc = {
            "title": problem.title,
            "description": problem.description,
            "difficulty": problem.difficulty,
            "language": problem.language,
            "test_cases": problem.test_cases,
            "starter_code": problem.starter_code,
            "hints": problem.hints or [],
            "created_by": str(current_user.id),
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Insert problem
        result = await db.coding_problems.insert_one(problem_doc)
        problem_doc["_id"] = result.inserted_id
        
        return CodingProblemResponse(
            problem_id=str(problem_doc["_id"]),
            title=problem_doc["title"],
            description=problem_doc["description"],
            difficulty=problem_doc["difficulty"],
            language=problem_doc["language"],
            test_cases=problem_doc["test_cases"],
            starter_code=problem_doc["starter_code"],
            hints=problem_doc["hints"],
            created_at=problem_doc["created_at"],
            is_active=problem_doc["is_active"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create coding problem: {str(e)}"
        )

@router.post("/execute", response_model=CodeExecutionResult)
async def execute_code(
    submission: CodeSubmission,
    current_user: UserModel = Depends(require_student_or_above)
):
    """Execute code and return results"""
    try:
        db = await get_db()
        
        # Get problem details
        problem_doc = await db.coding_problems.find_one({"_id": submission.problem_id})
        if not problem_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coding problem not found"
            )
        
        # Execute code using execution service
        execution_result = await code_execution_service.execute_code(
            code=submission.code,
            language=submission.language,
            test_cases=problem_doc["test_cases"]
        )
        
        # Calculate test results
        passed_tests = sum(1 for test in execution_result["test_results"] if test.get("passed", False))
        total_tests = len(execution_result["test_results"])
        
        # Create submission record
        submission_doc = {
            "problem_id": submission.problem_id,
            "student_id": str(current_user.id),
            "code": submission.code,
            "language": submission.language,
            "test_results": execution_result["test_results"],
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "execution_time": execution_result.get("execution_time", 0.0),
            "memory_usage": execution_result.get("memory_usage", 0.0),
            "status": "success" if execution_result.get("success", False) else "error",
            "submitted_at": datetime.utcnow()
        }
        
        # Insert submission
        result = await db.code_submissions.insert_one(submission_doc)
        submission_doc["_id"] = result.inserted_id
        
        return CodeExecutionResult(
            submission_id=str(submission_doc["_id"]),
            problem_id=submission_doc["problem_id"],
            student_id=submission_doc["student_id"],
            code=submission_doc["code"],
            language=submission_doc["language"],
            test_results=submission_doc["test_results"],
            passed_tests=submission_doc["passed_tests"],
            total_tests=submission_doc["total_tests"],
            execution_time=submission_doc["execution_time"],
            memory_usage=submission_doc["memory_usage"],
            status=submission_doc["status"],
            submitted_at=submission_doc["submitted_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute code: {str(e)}"
        )

@router.get("/stats", response_model=CodingStatsResponse)
async def get_coding_stats(current_user: UserModel = Depends(require_student_or_above)):
    """Get coding statistics for current user"""
    try:
        db = await get_db()
        
        # Get user's coding stats
        total_problems = await db.coding_problems.count_documents({"is_active": True})
        
        # Get user's submissions
        user_submissions = db.code_submissions.find({"student_id": str(current_user.id)})
        problems_solved = set()
        total_score = 0
        submission_count = 0
        language_usage = {}
        
        async for submission in user_submissions:
            if submission["status"] == "success" and submission["passed_tests"] == submission["total_tests"]:
                problems_solved.add(submission["problem_id"])
            
            total_score += (submission["passed_tests"] / submission["total_tests"]) * 100
            submission_count += 1
            
            language = submission["language"]
            language_usage[language] = language_usage.get(language, 0) + 1
        
        average_score = total_score / submission_count if submission_count > 0 else 0
        favorite_language = max(language_usage.items(), key=lambda x: x[1])[0] if language_usage else "python"
        
        # Get difficulty distribution
        difficulty_distribution = {}
        async for problem in db.coding_problems.find({"is_active": True}):
            difficulty = problem["difficulty"]
            difficulty_distribution[difficulty] = difficulty_distribution.get(difficulty, 0) + 1
        
        return CodingStatsResponse(
            total_problems=total_problems,
            problems_solved=len(problems_solved),
            average_score=average_score,
            favorite_language=favorite_language,
            difficulty_distribution=difficulty_distribution
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coding stats: {str(e)}"
        )

@router.get("/submissions", response_model=List[CodeExecutionResult])
async def get_user_submissions(
    problem_id: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_student_or_above)
):
    """Get user's code submissions"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {"student_id": str(current_user.id)}
        if problem_id:
            filter_dict["problem_id"] = problem_id
        
        # Get submissions
        submissions_cursor = db.code_submissions.find(filter_dict).sort("submitted_at", -1)
        submissions = []
        
        async for submission_doc in submissions_cursor:
            submissions.append(CodeExecutionResult(
                submission_id=str(submission_doc["_id"]),
                problem_id=submission_doc["problem_id"],
                student_id=submission_doc["student_id"],
                code=submission_doc["code"],
                language=submission_doc["language"],
                test_results=submission_doc["test_results"],
                passed_tests=submission_doc["passed_tests"],
                total_tests=submission_doc["total_tests"],
                execution_time=submission_doc["execution_time"],
                memory_usage=submission_doc["memory_usage"],
                status=submission_doc["status"],
                submitted_at=submission_doc["submitted_at"]
            ))
        
        return submissions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submissions: {str(e)}"
        )
