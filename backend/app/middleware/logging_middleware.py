"""
Logging Middleware
Middleware for automatic API request logging and audit trail
"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from ..services.structured_logging_service import get_structured_logger, LogLevel
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic request/response logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.structured_logger = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details"""
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Get structured logger
        if not self.structured_logger:
            from ...db import get_db
            db = await get_db()
            from ..services.structured_logging_service import initialize_logging
            self.structured_logger = initialize_logging(db)
        
        # Start timing
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        query_params = str(request.query_params)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Get user ID from request (if available)
        user_id = None
        if hasattr(request.state, 'user') and request.state.user:
            user_id = str(request.state.user.get("_id", ""))
        
        # Log request start
        await self.structured_logger.log_application_event(
            LogLevel.INFO,
            f"API Request Started: {method} {path}",
            {
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "user_id": user_id
            },
            user_id=user_id,
            request_id=request_id
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Get response details
            status_code = response.status_code
            response_size = len(response.body) if hasattr(response, 'body') else 0
            
            # Log successful request
            await self.structured_logger.log_api_request(
                method=method,
                path=path,
                user_id=user_id,
                request_id=request_id,
                status_code=status_code,
                response_time_ms=response_time_ms,
                request_size=0,  # Could be calculated from request body
                response_size=response_size,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Log performance metric
            await self.structured_logger.log_performance_metric(
                metric_name="api_response_time",
                value=response_time_ms,
                unit="ms",
                context={
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "user_id": user_id
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate response time for failed requests
            response_time_ms = (time.time() - start_time) * 1000
            
            # Log error
            await self.structured_logger.log_application_event(
                LogLevel.ERROR,
                f"API Request Failed: {method} {path}",
                {
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(e),
                    "response_time_ms": response_time_ms
                },
                user_id=user_id,
                request_id=request_id,
                exception=e
            )
            
            # Log security event if it's a potential security issue
            if status_code in [401, 403, 429]:
                await self.structured_logger.log_security_event(
                    event_type="api_access_denied",
                    user_id=user_id,
                    ip_address=ip_address,
                    details={
                        "method": method,
                        "path": path,
                        "status_code": status_code,
                        "error": str(e)
                    },
                    severity="medium"
                )
            
            raise

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic audit trail logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.structured_logger = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log audit events"""
        # Get structured logger
        if not self.structured_logger:
            from ...db import get_db
            db = await get_db()
            from ..services.structured_logging_service import initialize_logging
            self.structured_logger = initialize_logging(db)
        
        # Process request
        response = await call_next(request)
        
        # Log audit events for specific actions
        await self._log_audit_events(request, response)
        
        return response
    
    async def _log_audit_events(self, request: Request, response: Response):
        """Log audit events based on request/response"""
        try:
            # Get user ID
            user_id = None
            if hasattr(request.state, 'user') and request.state.user:
                user_id = str(request.state.user.get("_id", ""))
            
            # Get request details
            method = request.method
            path = request.url.path
            status_code = response.status_code
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            # Determine audit action based on path and method
            audit_action = self._determine_audit_action(method, path)
            
            if audit_action:
                # Extract resource details
                resource_id, resource_type = self._extract_resource_details(path)
                
                # Log audit event
                await self.structured_logger.log_audit_event(
                    action=audit_action,
                    user_id=user_id,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    details={
                        "method": method,
                        "path": path,
                        "status_code": status_code
                    },
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=200 <= status_code < 400
                )
                
        except Exception as e:
            logger.error(f"Failed to log audit events: {e}")
    
    def _determine_audit_action(self, method: str, path: str):
        """Determine audit action based on request method and path"""
        from ..services.structured_logging_service import AuditAction
        
        # Authentication actions
        if "/auth/login" in path and method == "POST":
            return AuditAction.USER_LOGIN
        elif "/auth/logout" in path and method == "POST":
            return AuditAction.USER_LOGOUT
        elif "/auth/register" in path and method == "POST":
            return AuditAction.USER_REGISTER
        
        # User management
        elif "/users/" in path and method == "PUT":
            return AuditAction.USER_UPDATE
        elif "/users/" in path and method == "DELETE":
            return AuditAction.USER_DELETE
        
        # Assessment actions
        elif "/assessments" in path and method == "POST":
            return AuditAction.ASSESSMENT_CREATE
        elif "/assessments/" in path and method == "PUT":
            return AuditAction.ASSESSMENT_UPDATE
        elif "/assessments/" in path and method == "DELETE":
            return AuditAction.ASSESSMENT_DELETE
        elif "/assessments/" in path and "/publish" in path and method == "POST":
            return AuditAction.ASSESSMENT_PUBLISH
        elif "/assessments/" in path and "/assign" in path and method == "POST":
            return AuditAction.ASSESSMENT_ASSIGN
        
        # Batch actions
        elif "/batches" in path and method == "POST":
            return AuditAction.BATCH_CREATE
        elif "/batches/" in path and method == "PUT":
            return AuditAction.BATCH_UPDATE
        elif "/batches/" in path and method == "DELETE":
            return AuditAction.BATCH_DELETE
        elif "/batches/" in path and "/students" in path and method == "POST":
            return AuditAction.BATCH_ADD_STUDENT
        elif "/batches/" in path and "/students" in path and method == "DELETE":
            return AuditAction.BATCH_REMOVE_STUDENT
        
        # Student actions
        elif "/assessments/" in path and "/submit" in path and method == "POST":
            return AuditAction.STUDENT_SUBMIT_ASSESSMENT
        elif "/assessments/" in path and method == "GET":
            return AuditAction.STUDENT_VIEW_ASSESSMENT
        
        # Admin actions
        elif "/admin/" in path:
            return AuditAction.ADMIN_USER_MANAGEMENT
        
        return None
    
    def _extract_resource_details(self, path: str):
        """Extract resource ID and type from path"""
        path_parts = path.strip("/").split("/")
        
        if len(path_parts) >= 2:
            resource_type = path_parts[0]
            resource_id = path_parts[1]
            return resource_id, resource_type
        
        return None, None

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring"""
    
    def __init__(self, app):
        super().__init__(app)
        self.structured_logger = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and monitor performance"""
        # Get structured logger
        if not self.structured_logger:
            from ...db import get_db
            db = await get_db()
            from ..services.structured_logging_service import initialize_logging
            self.structured_logger = initialize_logging(db)
        
        # Start timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate performance metrics
        response_time_ms = (time.time() - start_time) * 1000
        
        # Log performance metrics
        await self.structured_logger.log_performance_metric(
            metric_name="request_duration",
            value=response_time_ms,
            unit="ms",
            context={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code
            }
        )
        
        # Log slow requests
        if response_time_ms > 1000:  # More than 1 second
            await self.structured_logger.log_application_event(
                LogLevel.WARNING,
                f"Slow request detected: {request.method} {request.url.path}",
                {
                    "response_time_ms": response_time_ms,
                    "status_code": response.status_code
                }
            )
        
        return response
