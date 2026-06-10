from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from event_service import EventService
from schemas import EventCreateRequest, EventResponse
from exceptions import AppException

# Create router for event endpoints
router = APIRouter(
    prefix="/api/v1/events",
    tags=["events"],
    responses={
        400: {"description": "Bad request"},
        404: {"description": "Not found"},
        409: {"description": "Conflict"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/",
    response_model=EventResponse,
    status_code=201,
    summary="Create a new event",
    description="Create a new event with name, total seats, and date. All fields are required."
)
def create_event(
    event_data: EventCreateRequest,
    db: Session = Depends(get_db)
) -> EventResponse:
    """
    Create a new event.
    
    **Validation Rules:**
    - Event name must be unique
    - Total seats must be greater than 0
    - Event date must be in the future
    
    **Example Request:**
    ```json
    {
        "name": "Tech Conference 2024",
        "total_seats": 100,
        "event_date": "2024-12-15T10:00:00"
    }
    ```
    
    **Returns:**
    - 201: Event created successfully
    - 400: Validation error (invalid seats or date)
    - 409: Event name already exists
    """
    try:
        service = EventService(db)
        return service.create_event(event_data)
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.get(
    "/",
    response_model=List[EventResponse],
    summary="List all events",
    description="Retrieve all events with optional filtering and sorting."
)
def list_events(
    upcoming_only: bool = Query(
        False,
        description="Filter to show only upcoming events (date > now)"
    ),
    sort_by_date: bool = Query(
        False,
        description="Sort events by date in ascending order"
    ),
    db: Session = Depends(get_db)
) -> List[EventResponse]:
    """
    List all events with optional filtering and sorting.
    
    **Query Parameters:**
    - `upcoming_only`: If true, only return events with date in the future
    - `sort_by_date`: If true, sort by event_date in ascending order
    
    **Example Requests:**
    - GET /api/v1/events
    - GET /api/v1/events?upcoming_only=true
    - GET /api/v1/events?sort_by_date=true
    - GET /api/v1/events?upcoming_only=true&sort_by_date=true
    
    **Returns:**
    - 200: List of events with calculated available seats and registration counts
    """
    try:
        service = EventService(db)
        return service.list_events(
            upcoming_only=upcoming_only,
            sort_by_date=sort_by_date
        )
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event details",
    description="Retrieve details for a specific event including available seats."
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
) -> EventResponse:
    """
    Get details for a specific event.
    
    **Path Parameters:**
    - `event_id`: The ID of the event to retrieve
    
    **Example Request:**
    - GET /api/v1/events/1
    
    **Returns:**
    - 200: Event details including available seats and registration count
    - 404: Event not found
    """
    try:
        service = EventService(db)
        return service.get_event(event_id)
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )