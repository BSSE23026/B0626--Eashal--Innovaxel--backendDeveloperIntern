from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from registration_service import RegistrationService
from schemas import (
    RegistrationCreateRequest,
    RegistrationResponse,
    RegistrationCancelRequest
)
from exceptions import AppException

# Create router for registration endpoints
router = APIRouter(
    prefix="/api/v1/registrations",
    tags=["registrations"],
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Not found"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/",
    response_model=RegistrationResponse,
    status_code=201,
    summary="Register user for an event",
    description="Register a user for an event with race condition protection and duplicate detection."
)
def register_user(
    registration_data: RegistrationCreateRequest,
    db: Session = Depends(get_db)
) -> RegistrationResponse:
    """
    Register a user for an event.
    
    **Features:**
    - Prevents race conditions using database-level locks
    - Prevents duplicate registrations for the same user and event
    - Prevents overbooking when event is full
    - Stores registration timestamp automatically
    
    **Validation Rules:**
    - Cannot register if event is full
    - Same user cannot register twice for the same event
    - Event must exist
    
    **Example Request:**
    ```json
    {
        "username": "john_doe",
        "event_id": 1
    }
    ```
    
    **Returns:**
    - 201: User registered successfully
    - 404: Event not found
    - 409: Event is full or user already registered
    """
    try:
        service = RegistrationService(db)
        return service.register_user(registration_data)
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.get(
    "/",
    response_model=List[RegistrationResponse],
    summary="List all registrations",
    description="Retrieve all active registrations in the system."
)
def list_registrations(
    db: Session = Depends(get_db)
) -> List[RegistrationResponse]:
    """
    List all active registrations in the system.
    
    **Returns:**
    - 200: List of all active registrations
    
    Note: Cancelled registrations are not included in this list.
    """
    # Query all active registrations
    from models import Registration
    registrations = db.query(Registration).filter(
        Registration.is_active == 1
    ).order_by(Registration.registered_at.desc()).all()
    
    service = RegistrationService(db)
    return [service._registration_to_response(reg) for reg in registrations]


@router.get(
    "/{registration_id}",
    response_model=RegistrationResponse,
    summary="Get registration details",
    description="Retrieve details for a specific registration."
)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db)
) -> RegistrationResponse:
    """
    Get details for a specific registration.
    
    **Path Parameters:**
    - `registration_id`: The ID of the registration
    
    **Example Request:**
    - GET /api/v1/registrations/42
    
    **Returns:**
    - 200: Registration details
    - 404: Registration not found
    """
    try:
        service = RegistrationService(db)
        return service.get_registration(registration_id)
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.get(
    "/event/{event_id}",
    response_model=List[RegistrationResponse],
    summary="Get registrations for an event",
    description="Retrieve all active registrations for a specific event."
)
def get_event_registrations(
    event_id: int,
    db: Session = Depends(get_db)
) -> List[RegistrationResponse]:
    """
    Get all active registrations for a specific event.
    
    **Path Parameters:**
    - `event_id`: The ID of the event
    
    **Example Request:**
    - GET /api/v1/registrations/event/1
    
    **Returns:**
    - 200: List of active registrations for the event
    - 404: Event not found
    
    Note: Only active (non-cancelled) registrations are returned.
    """
    try:
        service = RegistrationService(db)
        return service.get_event_registrations(event_id, active_only=True)
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.delete(
    "/{registration_id}",
    response_model=RegistrationResponse,
    summary="Cancel a registration",
    description="Cancel a user's registration and free up the seat."
)
def cancel_registration(
    registration_id: int,
    db: Session = Depends(get_db)
) -> RegistrationResponse:
    """
    Cancel a registration.
    
    **Features:**
    - Soft delete approach (marks as cancelled, doesn't remove)
    - Seat becomes available again for other users
    - Cancelled registrations don't appear in active registrations
    
    **Rules:**
    - Registration must exist
    - Registration must not already be cancelled
    
    **Path Parameters:**
    - `registration_id`: The ID of the registration to cancel
    
    **Example Request:**
    - DELETE /api/v1/registrations/42
    
    **Returns:**
    - 200: Registration cancelled successfully
    - 404: Registration not found
    - 400: Registration already cancelled
    """
    try:
        service = RegistrationService(db)
        return service.cancel_registration(registration_id)
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )