from typing import Any, Dict, Optional

class KhetiPulseException(Exception):
    """Base exception for KhetiPulse application."""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        self.extra = extra
        super().__init__(self.message)

class ExternalServiceError(KhetiPulseException):
    """Raised when an external service (AWS, Agmarknet, etc.) fails."""
    def __init__(self, service_name: str, detail: Optional[str] = None):
        super().__init__(
            message=f"Error communicating with {service_name}",
            status_code=502,
            detail=detail
        )

class ResourceNotFoundError(KhetiPulseException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with ID {identifier} not found",
            status_code=404
        )

class ValidationException(KhetiPulseException):
    """Raised when request validation fails beyond Pydantic's scope."""
    def __init__(self, detail: str):
        super().__init__(message=detail, status_code=400)
