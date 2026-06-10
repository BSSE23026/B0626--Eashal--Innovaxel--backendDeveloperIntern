from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import Event, Registration
from schemas import EventCreateRequest, EventResponse
from exceptions import (
    EventNotFoundError,
    DuplicateEventNameError,
    InvalidEventDateError,
    InvalidSeatsError
)


class EventService:
    """
    Service class for event-related operations.
    Encapsulates business logic and database interactions for events.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the event service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_event(self, event_data: EventCreateRequest) -> EventResponse:
        """
        Create a new event with validation.
        
        Args:
            event_data: EventCreateRequest containing event details
            
        Returns:
            EventResponse: The created event
            
        Raises:
            InvalidSeatsError: If total_seats <= 0
            InvalidEventDateError: If event_date is not in future
            DuplicateEventNameError: If event name already exists
        """
        # Validation: total_seats must be greater than 0
        if event_data.total_seats <= 0:
            raise InvalidSeatsError()
        
        # Validation: event_date must be in the future
        if event_data.event_date <= datetime.utcnow():
            raise InvalidEventDateError()
        
        # Create new event instance
        db_event = Event(
            name=event_data.name,
            total_seats=event_data.total_seats,
            event_date=event_data.event_date
        )
        
        try:
            # Add to database
            self.db.add(db_event)
            self.db.commit()
            self.db.refresh(db_event)
        except IntegrityError:
            # Handle unique constraint violation on event name
            self.db.rollback()
            raise DuplicateEventNameError(event_data.name)
        
        return self._event_to_response(db_event)
    
    def get_event(self, event_id: int) -> EventResponse:
        """
        Retrieve a single event by ID.
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            EventResponse: The event data
            
        Raises:
            EventNotFoundError: If event doesn't exist
        """
        db_event = self.db.query(Event).filter(Event.id == event_id).first()
        
        if not db_event:
            raise EventNotFoundError(event_id)
        
        return self._event_to_response(db_event)
    
    def list_events(
        self,
        upcoming_only: bool = False,
        sort_by_date: bool = False
    ) -> List[EventResponse]:
        """
        List all events with optional filtering and sorting.
        
        Args:
            upcoming_only: If True, only return events with date > now
            sort_by_date: If True, sort by event_date ascending
            
        Returns:
            List[EventResponse]: List of events
        """
        query = self.db.query(Event)
        
        # Filter: upcoming events only
        if upcoming_only:
            now = datetime.utcnow()
            query = query.filter(Event.event_date > now)
        
        # Sort: by event date
        if sort_by_date:
            query = query.order_by(Event.event_date.asc())
        else:
            # Default: sort by creation date (newest first)
            query = query.order_by(Event.created_at.desc())
        
        events = query.all()
        return [self._event_to_response(event) for event in events]
    
    def _event_to_response(self, db_event: Event) -> EventResponse:
        """
        Convert database event model to response schema.
        Calculates available seats and total registrations.
        
        Args:
            db_event: Event database model
            
        Returns:
            EventResponse: Response schema with calculated fields
        """
        # Count active registrations (is_active = 1)
        active_registrations = self.db.query(Registration).filter(
            Registration.event_id == db_event.id,
            Registration.is_active == 1
        ).count()
        
        # Calculate available seats
        available_seats = db_event.total_seats - active_registrations
        
        return EventResponse(
            id=db_event.id,
            name=db_event.name,
            total_seats=db_event.total_seats,
            event_date=db_event.event_date,
            available_seats=available_seats,
            total_registrations=active_registrations,
            created_at=db_event.created_at
        )