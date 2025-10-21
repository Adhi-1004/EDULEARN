"""
Validation Decorators
Decorators for validating API endpoints and request data
"""
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from fastapi import HTTPException, Request
from pydantic import BaseModel, ValidationError
import logging
from ..services.validation_service import ValidationService

logger = logging.getLogger(__name__)

def validate_request_data(validation_model: BaseModel):
    """Decorator to validate request data using Pydantic models"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Extract request from args
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if not request:
                    raise HTTPException(status_code=400, detail="Request object not found")
                
                # Parse and validate request body
                body = await request.json()
                validated_data = validation_model(**body)
                
                # Replace request body with validated data
                request._body = validated_data.dict()
                
                return await func(*args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Validation error: {e}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid request data",
                        "details": e.errors()
                    }
                )
            except Exception as e:
                logger.error(f"Unexpected error in validation decorator: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        return wrapper
    return decorator

def validate_query_params(**param_validators):
    """Decorator to validate query parameters"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Extract request from args
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if not request:
                    raise HTTPException(status_code=400, detail="Request object not found")
                
                # Validate query parameters
                for param_name, validator in param_validators.items():
                    param_value = request.query_params.get(param_name)
                    if param_value is not None:
                        validation_result = validator(param_value)
                        if not validation_result["is_valid"]:
                            raise HTTPException(
                                status_code=400,
                                detail={
                                    "success": False,
                                    "error": "Validation Error",
                                    "message": f"Invalid {param_name}",
                                    "details": validation_result["errors"]
                                }
                            )
                
                return await func(*args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in query validation decorator: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        return wrapper
    return decorator

def validate_path_params(**param_validators):
    """Decorator to validate path parameters"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Extract request from args
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if not request:
                    raise HTTPException(status_code=400, detail="Request object not found")
                
                # Validate path parameters
                for param_name, validator in param_validators.items():
                    param_value = request.path_params.get(param_name)
                    if param_value is not None:
                        validation_result = validator(param_value)
                        if not validation_result["is_valid"]:
                            raise HTTPException(
                                status_code=400,
                                detail={
                                    "success": False,
                                    "error": "Validation Error",
                                    "message": f"Invalid {param_name}",
                                    "details": validation_result["errors"]
                                }
                            )
                
                return await func(*args, **kwargs)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in path validation decorator: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        return wrapper
    return decorator

def validate_assessment_creation(func: Callable):
    """Decorator specifically for assessment creation validation"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(status_code=400, detail="Request object not found")
            
            # Parse request body
            body = await request.json()
            
            # Validate assessment data
            validation_service = ValidationService()
            
            # Validate title
            title = body.get("title", "")
            title_validation = validation_service.validate_assessment_title(title)
            if not title_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid assessment title",
                        "details": title_validation["errors"]
                    }
                )
            
            # Validate description
            description = body.get("description", "")
            desc_validation = validation_service.validate_assessment_description(description)
            if not desc_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid assessment description",
                        "details": desc_validation["errors"]
                    }
                )
            
            # Validate time limit
            time_limit = body.get("time_limit", 0)
            time_validation = validation_service.validate_time_limit(time_limit)
            if not time_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid time limit",
                        "details": time_validation["errors"]
                    }
                )
            
            # Validate question count
            question_count = body.get("question_count", 0)
            qcount_validation = validation_service.validate_question_count(question_count)
            if not qcount_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid question count",
                        "details": qcount_validation["errors"]
                    }
                )
            
            # Validate batch assignment
            batch_ids = body.get("batches", [])
            batch_validation = validation_service.validate_batch_assignment(batch_ids)
            if not batch_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid batch assignment",
                        "details": batch_validation["errors"]
                    }
                )
            
            return await func(*args, **kwargs)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in assessment validation decorator: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return wrapper

def validate_batch_creation(func: Callable):
    """Decorator specifically for batch creation validation"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(status_code=400, detail="Request object not found")
            
            # Parse request body
            body = await request.json()
            
            # Validate batch data
            validation_service = ValidationService()
            
            # Validate batch name
            name = body.get("name", "")
            name_validation = validation_service.validate_batch_name(name)
            if not name_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid batch name",
                        "details": name_validation["errors"]
                    }
                )
            
            return await func(*args, **kwargs)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in batch validation decorator: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return wrapper

def validate_student_creation(func: Callable):
    """Decorator specifically for student creation validation"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(status_code=400, detail="Request object not found")
            
            # Parse request body
            body = await request.json()
            
            # Validate student data
            validation_service = ValidationService()
            
            student_data = {
                "name": body.get("student_name", ""),
                "email": body.get("student_email", "")
            }
            student_validation = validation_service.validate_student_data(student_data)
            if not student_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid student data",
                        "details": student_validation["errors"]
                    }
                )
            
            return await func(*args, **kwargs)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in student validation decorator: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return wrapper

def validate_bulk_upload(func: Callable):
    """Decorator specifically for bulk upload validation"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(status_code=400, detail="Request object not found")
            
            # Parse request body
            body = await request.json()
            
            # Validate bulk upload data
            validation_service = ValidationService()
            
            students_data = body.get("students", [])
            bulk_validation = validation_service.validate_bulk_upload_data(students_data)
            if not bulk_validation["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Validation Error",
                        "message": "Invalid bulk upload data",
                        "details": bulk_validation["errors"]
                    }
                )
            
            return await func(*args, **kwargs)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in bulk upload validation decorator: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return wrapper

def validate_search_query(func: Callable):
    """Decorator specifically for search query validation"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Extract request from args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(status_code=400, detail="Request object not found")
            
            # Validate search query
            validation_service = ValidationService()
            
            query = request.query_params.get("q", "")
            if query:
                search_validation = validation_service.validate_search_query(query)
                if not search_validation["is_valid"]:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "success": False,
                            "error": "Validation Error",
                            "message": "Invalid search query",
                            "details": search_validation["errors"]
                        }
                    )
            
            return await func(*args, **kwargs)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in search validation decorator: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return wrapper
