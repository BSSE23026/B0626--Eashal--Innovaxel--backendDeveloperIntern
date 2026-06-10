from typing import Optional


class AppException(Exception):
    """
    Base exception class for all application exceptions.
    
    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


# ==================== Event-Related Exceptions ====================

class EventNotFoundError(AppException):
    """Raised when an event is not found."""
    
    def __init__(self, event_id: int):
        super().__init__(
            message=f"Event with ID {event_id} not found",
            error_code="EVENT_NOT_FOUND",
            status_code=404
        )


class DuplicateEventNameError(AppException):
    """Raised when trying to create an event with a duplicate name."""
    
    def __init__(self, event_name: str):
        super().__init__(
            message=f"Event with name '{event_name}' already exists",
            error_code="DUPLICATE_EVENT_NAME",
            status_code=409
        )


class InvalidEventDateError(AppException):
    """Raised when event date is not in the future."""
    
    def __init__(self):
        super().__init__(
            message="Event date must be in the future",
            error_code="INVALID_EVENT_DATE",
            status_code=400
        )


class InvalidSeatsError(AppException):
    """Raised when total seats is not greater than 0."""
    
    def __init__(self):
        super().__init__(
            message="Total seats must be greater than 0",
            error_code="INVALID_SEATS",
            status_code=400
        )


# ==================== Registration-Related Exceptions ====================

class EventFullError(AppException):
    """Raised when trying to register for a full event."""
    
    def __init__(self, event_id: int):
        super().__init__(
            message=f"Event {event_id} is full and no seats are available",
            error_code="EVENT_FULL",
            status_code=409
        )


class DuplicateRegistrationError(AppException):
    """Raised when a user tries to register twice for the same event."""
    
    def __init__(self, username: str, event_id: int):
        super().__init__(
            message=f"User '{username}' is already registered for event {event_id}",
            error_code="DUPLICATE_REGISTRATION",
            status_code=409
        )


class RegistrationNotFoundError(AppException):
    """Raised when a registration is not found."""
    
    def __init__(self, registration_id: int):
        super().__init__(
            message=f"Registration with ID {registration_id} not found",
            error_code="REGISTRATION_NOT_FOUND",
            status_code=404
        )


class InvalidRegistrationError(AppException):
    """Raised when a registration is invalid or already cancelled."""
    
    def __init__(self, registration_id: int):
        super().__init__(
            message=f"Registration {registration_id} is invalid or already cancelled",
            error_code="INVALID_REGISTRATION",
            status_code=400
        )


# ==================== Validation Exceptions ====================

class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400
        )