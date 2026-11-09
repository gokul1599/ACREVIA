"""
ACREVIA - Domain & Application Exceptions.
"""

from typing import Optional, Dict, Any


class AcreviaException(Exception):
    """Base exception for all ACREVIA domain errors."""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.headers = headers or {}


class EntityNotFoundException(AcreviaException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=404,
            details={"entity": entity_name, "identifier": str(identifier)}
        )


class NotFoundException(AcreviaException):
    def __init__(self, message: str = "Requested resource was not found."):
        super().__init__(message=message, status_code=404)


class AuthorizationException(AcreviaException):
    """Raised when a user attempts cross-farm access or unauthorized resource mutation."""
    def __init__(self, message: str = "Access to requested agricultural resource is forbidden."):
        super().__init__(message=message, status_code=403)


class AuthenticationException(AcreviaException):
    def __init__(self, message: str = "Could not validate authentication credentials."):
        super().__init__(message=message, status_code=401)


class ConflictException(AcreviaException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=409)


class ValidationException(AcreviaException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=400, details=details)


class ServiceUnavailableException(AcreviaException):
    def __init__(self, service_name: str, message: str = "Service is currently unavailable.", retry_after: int = 30):
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=503,
            details={"service": service_name, "retry_after_seconds": retry_after},
            headers={"Retry-After": str(retry_after)}
        )
        self.retry_after = retry_after


class RateLimitExceededException(AcreviaException):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=429,
            details={"retry_after_seconds": retry_after},
            headers={"Retry-After": str(retry_after)}
        )
        self.retry_after = retry_after


# Convenient Aliases for Service Layer Consistency
NotFoundError = NotFoundException
ValidationError = ValidationException
AuthorizationError = AuthorizationException
PermissionDeniedError = AuthorizationException
AuthenticationError = AuthenticationException
ConflictError = ConflictException
ServiceUnavailableError = ServiceUnavailableException


