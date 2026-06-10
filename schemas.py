from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ==================== Event Schemas ====================

class EventCreateRequest(BaseModel):
    """
    Schema for creating a new event.
    
    Validation Rules:
        - name: Required, non-empty string, max 255 characters
        - total_seats: Required, must be greater than 0
        - event_date: Required, must be a valid datetime in the future
    """
    name: str = Field(..., min_length=1, max_length=255, description="Unique event name")
    total_seats: int = Field(..., gt=0, description="Total number of seats for the event")
    event_date: datetime = Field(..., description="Date and time of the event (must be in future)")
    
    @field_validator('event_date')
    @classmethod
    def validate_future_date(cls, v: datetime) -> datetime:
        """Ensure event_date is in the future."""
        if v <= datetime.utcnow():
            raise ValueError("Event date must be in the future")
        return v


class EventResponse(BaseModel):
    """
    Schema for event response data.
    Includes calculated fields like available seats and registration count.
    """
    id: int = Field(..., description="Event ID")
    name: str = Field(..., description="Event name")
    total_seats: int = Field(..., description="Total number of seats")
    event_date: datetime = Field(..., description="Event date and time")
    available_seats: int = Field(..., description="Number of available seats (calculated)")
    total_registrations: int = Field(..., description="Total number of active registrations")
    created_at: datetime = Field(..., description="Event creation timestamp")
    
    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    """Extended event response with additional details."""
    registrations: list['RegistrationResponse'] = Field(default_factory=list)


# ==================== Registration Schemas ====================

class RegistrationCreateRequest(BaseModel):
    """
    Schema for registering a user for an event.
    
    Validation Rules:
        - username: Required, non-empty string, max 255 characters
        - event_id: Required, must be positive integer
    """
    username: str = Field(..., min_length=1, max_length=255, description="Name of the user")
    event_id: int = Field(..., gt=0, description="ID of the event to register for")


class RegistrationResponse(BaseModel):
    """Schema for registration response data."""
    id: int = Field(..., description="Registration ID")
    event_id: int = Field(..., description="Event ID")
    username: str = Field(..., description="Registered user's name")
    registered_at: datetime = Field(..., description="Registration timestamp")
    is_active: int = Field(..., description="1 = active, 0 = cancelled")
    
    class Config:
        from_attributes = True


class RegistrationCancelRequest(BaseModel):
    """Schema for cancelling a registration."""
    registration_id: int = Field(..., gt=0, description="ID of the registration to cancel")


# ==================== Generic Response Schemas ====================

class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = Field(True, description="Indicates successful operation")
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Response data")


# Update forward references for self-referential relationships
EventDetailResponse.model_rebuild()