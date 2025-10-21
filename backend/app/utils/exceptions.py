"""
Custom Exception Classes
Centralized error handling with specific exception types
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class EduLearnException(Exception):
    """Base exception for EduLearn application"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERIC_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(EduLearnException):
    """Validation error exception"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details or {"field": field},
            status_code=status.HTTP_400_BAD_REQUEST
        )

class AuthenticationError(EduLearnException):
    """Authentication error exception"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AuthorizationError(EduLearnException):
    """Authorization error exception"""
    
    def __init__(
        self,
        message: str = "Access denied",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )

class NotFoundError(EduLearnException):
    """Resource not found exception"""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details or {"resource_type": resource_type, "resource_id": resource_id},
            status_code=status.HTTP_404_NOT_FOUND
        )

class ConflictError(EduLearnException):
    """Resource conflict exception"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=details,
            status_code=status.HTTP_409_CONFLICT
        )

class DatabaseError(EduLearnException):
    """Database operation error exception"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details or {"operation": operation},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ExternalServiceError(EduLearnException):
    """External service error exception"""
    
    def __init__(
        self,
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=f"{service_name} service error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details or {"service_name": service_name},
            status_code=status.HTTP_502_BAD_GATEWAY
        )

class RateLimitError(EduLearnException):
    """Rate limit exceeded exception"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details or {"retry_after": retry_after},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )

class BusinessLogicError(EduLearnException):
    """Business logic error exception"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details or {"operation": operation},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

# Specific business exceptions
class BatchNotFoundError(NotFoundError):
    """Batch not found exception"""
    
    def __init__(self, batch_id: str):
        super().__init__("Batch", batch_id)

class StudentNotFoundError(NotFoundError):
    """Student not found exception"""
    
    def __init__(self, student_id: str):
        super().__init__("Student", student_id)

class AssessmentNotFoundError(NotFoundError):
    """Assessment not found exception"""
    
    def __init__(self, assessment_id: str):
        super().__init__("Assessment", assessment_id)

class TeacherNotFoundError(NotFoundError):
    """Teacher not found exception"""
    
    def __init__(self, teacher_id: str):
        super().__init__("Teacher", teacher_id)

class BatchHasNoStudentsError(BusinessLogicError):
    """Batch has no students exception"""
    
    def __init__(self, batch_id: str):
        super().__init__(
            f"Batch {batch_id} has no students assigned",
            "batch_validation"
        )

class AssessmentAlreadySubmittedError(ConflictError):
    """Assessment already submitted exception"""
    
    def __init__(self, assessment_id: str, student_id: str):
        super().__init__(
            f"Assessment {assessment_id} already submitted by student {student_id}",
            {"assessment_id": assessment_id, "student_id": student_id}
        )

class InvalidAssessmentStatusError(BusinessLogicError):
    """Invalid assessment status exception"""
    
    def __init__(self, assessment_id: str, current_status: str, required_status: str):
        super().__init__(
            f"Assessment {assessment_id} has status '{current_status}', but '{required_status}' is required",
            "assessment_status_validation",
            {
                "assessment_id": assessment_id,
                "current_status": current_status,
                "required_status": required_status
            }
        )

class DuplicateNotificationError(ConflictError):
    """Duplicate notification exception"""
    
    def __init__(self, notification_type: str, student_id: str):
        super().__init__(
            f"Duplicate {notification_type} notification for student {student_id}",
            {"notification_type": notification_type, "student_id": student_id}
        )

class AIServiceError(ExternalServiceError):
    """AI service error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("AI", message, details)

class CodeExecutionError(ExternalServiceError):
    """Code execution service error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("Code Execution", message, details)

class NotificationDeliveryError(ExternalServiceError):
    """Notification delivery error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("Notification", message, details)
