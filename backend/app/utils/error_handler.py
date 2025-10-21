"""
Error Handling Middleware
Centralized error handling and response formatting
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
from typing import Union
from .exceptions import (
    EduLearnException, ValidationError, AuthenticationError, AuthorizationError,
    NotFoundError, ConflictError, DatabaseError, ExternalServiceError,
    RateLimitError, BusinessLogicError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def edu_learn_exception_handler(request: Request, exc: EduLearnException) -> JSONResponse:
    """Handle custom EduLearn exceptions"""
    logger.error(f"EduLearn Exception: {exc.error_code} - {exc.message}")
    logger.error(f"Details: {exc.details}")
    logger.error(f"Request: {request.method} {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": exc.details.get("timestamp", "unknown")
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    logger.warning(f"Request: {request.method} {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {"status_code": exc.status_code},
                "timestamp": "unknown"
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    logger.warning(f"Validation Error: {exc.errors()}")
    logger.warning(f"Request: {request.method} {request.url}")
    
    # Format validation errors
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "validation_errors": formatted_errors
                },
                "timestamp": "unknown"
            }
        }
    )

async def starlette_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions"""
    logger.warning(f"Starlette HTTP Exception: {exc.status_code} - {exc.detail}")
    logger.warning(f"Request: {request.method} {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"STARLETTE_{exc.status_code}",
                "message": exc.detail,
                "details": {"status_code": exc.status_code},
                "timestamp": "unknown"
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(f"Unhandled Exception: {type(exc).__name__} - {str(exc)}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Don't expose internal errors in production
    error_message = "Internal server error"
    error_details = {}
    
    # In development, include more details
    if logger.level <= logging.DEBUG:
        error_message = str(exc)
        error_details = {
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": error_message,
                "details": error_details,
                "timestamp": "unknown"
            }
        }
    )

def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app"""
    
    # Custom exception handlers
    app.add_exception_handler(EduLearnException, edu_learn_exception_handler)
    
    # Standard exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully")

class ErrorContext:
    """Context manager for error handling with additional context"""
    
    def __init__(self, operation: str, **context):
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            logger.info(f"Operation completed: {self.operation} (took {duration:.2f}s)")
        else:
            logger.error(f"Operation failed: {self.operation} (took {duration:.2f}s)")
            logger.error(f"Exception: {exc_type.__name__}: {exc_val}")
            
            # Add context to exception if it's an EduLearnException
            if isinstance(exc_val, EduLearnException):
                exc_val.details.update(self.context)
                exc_val.details["operation"] = self.operation
                exc_val.details["duration"] = duration
        
        return False  # Don't suppress the exception

def handle_database_error(operation: str, error: Exception) -> EduLearnException:
    """Convert database errors to EduLearn exceptions"""
    error_message = f"Database operation failed: {operation}"
    
    if "duplicate key" in str(error).lower():
        return ConflictError(
            f"Resource already exists for operation: {operation}",
            {"operation": operation, "original_error": str(error)}
        )
    elif "not found" in str(error).lower():
        return NotFoundError(
            "Database resource",
            details={"operation": operation, "original_error": str(error)}
        )
    else:
        return DatabaseError(
            error_message,
            operation,
            {"original_error": str(error)}
        )

def handle_validation_error(field: str, message: str, value: any = None) -> ValidationError:
    """Create a validation error with proper formatting"""
    return ValidationError(
        message=message,
        field=field,
        details={"value": str(value) if value is not None else None}
    )

def handle_external_service_error(service_name: str, error: Exception) -> ExternalServiceError:
    """Convert external service errors to EduLearn exceptions"""
    return ExternalServiceError(
        service_name=service_name,
        message=str(error),
        details={"original_error": str(error)}
    )

# Import time for ErrorContext
import time
