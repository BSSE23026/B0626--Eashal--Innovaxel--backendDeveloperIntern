from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError

from models import Event, Registration
from schemas import RegistrationCreateRequest, RegistrationResponse
from exceptions import (
    EventNotFoundError,
    EventFullError,
    DuplicateRegistrationError,
    RegistrationNotFoundError,
    InvalidRegistrationError,
    ValidationError
)


class RegistrationService:
    """
    Service class for registration-related operations.
    Implements thread-safe registration logic to prevent race conditions.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the registration service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def register_user(self, registration_data: RegistrationCreateRequest) -> RegistrationResponse:
        """
        Register a user for an event with race condition protection.
        
        This method implements atomic operations to prevent:
        1. Overbooking (registering when event is full)
        2. Duplicate registrations (same user registering twice)
        3. Race conditions (multiple concurrent registrations)
        
        The strategy:
        - Use database transaction with proper isolation
        - Lock the event row using SELECT FOR UPDATE
        - Check availability and register atomically
        - Let database constraints catch any conflicts
        
        Args:
            registration_data: RegistrationCreateRequest containing user and event info
            
        Returns:
            RegistrationResponse: The created registration
            
        Raises:
            EventNotFoundError: If event doesn't exist
            EventFullError: If event is full
            DuplicateRegistrationError: If user already registered for this event
            ValidationError: If validation fails
        """
        
        # Validate input
        if not registration_data.username.strip():
            raise ValidationError("Username cannot be empty")
        
        try:
            # Step 1: Lock the event row to prevent concurrent modifications
            # Using SELECT FOR UPDATE ensures exclusive lock on the event
            event = self.db.query(Event).filter(
                Event.id == registration_data.event_id
            ).with_for_update().first()
            
            # Step 2: Check if event exists
            if not event:
                raise EventNotFoundError(registration_data.event_id)
            
            # Step 3: Count current active registrations for this event
            active_registration_count = self.db.query(func.count(Registration.id)).filter(
                and_(
                    Registration.event_id == registration_data.event_id,
                    Registration.is_active == 1
                )
            ).scalar()
            
            # Step 4: Check if event is full
            if active_registration_count >= event.total_seats:
                raise EventFullError(registration_data.event_id)
            
            # Step 5: Check if user already has an active registration for this event
            existing_registration = self.db.query(Registration).filter(
                and_(
                    Registration.event_id == registration_data.event_id,
                    Registration.username == registration_data.username,
                    Registration.is_active == 1
                )
            ).first()
            
            if existing_registration:
                raise DuplicateRegistrationError(
                    registration_data.username,
                    registration_data.event_id
                )
            
            # Step 6: Create new registration
            # The database transaction ensures this completes atomically
            registration = Registration(
                event_id=registration_data.event_id,
                username=registration_data.username,
                is_active=1
            )
            
            self.db.add(registration)
            self.db.flush()  # Flush to database but don't commit yet
            
            # Step 7: Commit the transaction
            # If another thread has already filled the event, IntegrityError will occur
            self.db.commit()
            self.db.refresh(registration)
            
            return self._registration_to_response(registration)
        
        except EventFullError:
            self.db.rollback()
            raise
        except DuplicateRegistrationError:
            self.db.rollback()
            raise
        except EventNotFoundError:
            self.db.rollback()
            raise
        except IntegrityError as e:
            """
            Handle database constraint violations.
            This catches race conditions that weren't prevented by row-level locks.
            Could happen if:
            1. Unique constraint on (event_id, username) is violated
            2. Another thread just filled the event
            """
            self.db.rollback()
            
            # Check if it's a duplicate registration constraint violation
            if "unique_active_registration" in str(e):
                raise DuplicateRegistrationError(
                    registration_data.username,
                    registration_data.event_id
                )
            else:
                # General constraint violation, likely due to race condition
                raise EventFullError(registration_data.event_id)
        except ValidationError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise
    
    def cancel_registration(self, registration_id: int) -> RegistrationResponse:
        """
        Cancel a user's registration and free up the seat.
        
        Rules:
        - Sets is_active to 0 (soft delete)
        - Seat becomes available again
        - Cancelled registrations don't appear in active registrations
        
        Args:
            registration_id: ID of the registration to cancel
            
        Returns:
            RegistrationResponse: The cancelled registration
            
        Raises:
            RegistrationNotFoundError: If registration doesn't exist
            InvalidRegistrationError: If registration is already cancelled
        """
        
        # Fetch the registration
        registration = self.db.query(Registration).filter(
            Registration.id == registration_id
        ).first()
        
        # Check if registration exists
        if not registration:
            raise RegistrationNotFoundError(registration_id)
        
        # Check if already cancelled
        if registration.is_active == 0:
            raise InvalidRegistrationError(registration_id)
        
        # Cancel the registration (soft delete)
        registration.is_active = 0
        
        self.db.commit()
        self.db.refresh(registration)
        
        return self._registration_to_response(registration)
    
    def get_registration(self, registration_id: int) -> RegistrationResponse:
        """
        Retrieve a single registration by ID.
        
        Args:
            registration_id: ID of the registration
            
        Returns:
            RegistrationResponse: The registration data
            
        Raises:
            RegistrationNotFoundError: If registration doesn't exist
        """
        
        registration = self.db.query(Registration).filter(
            Registration.id == registration_id
        ).first()
        
        if not registration:
            raise RegistrationNotFoundError(registration_id)
        
        return self._registration_to_response(registration)
    
    def get_event_registrations(
        self,
        event_id: int,
        active_only: bool = True
    ) -> List[RegistrationResponse]:
        """
        Get all registrations for a specific event.
        
        Args:
            event_id: ID of the event
            active_only: If True, only return active registrations
            
        Returns:
            List[RegistrationResponse]: List of registrations
            
        Raises:
            EventNotFoundError: If event doesn't exist
        """
        
        # Verify event exists
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise EventNotFoundError(event_id)
        
        # Query registrations
        query = self.db.query(Registration).filter(
            Registration.event_id == event_id
        )
        
        if active_only:
            query = query.filter(Registration.is_active == 1)
        
        # Sort by registration date
        query = query.order_by(Registration.registered_at.asc())
        
        registrations = query.all()
        return [self._registration_to_response(reg) for reg in registrations]
    
    def _registration_to_response(self, registration: Registration) -> RegistrationResponse:
        """
        Convert database registration model to response schema.
        
        Args:
            registration: Registration database model
            
        Returns:
            RegistrationResponse: Response schema
        """
        return RegistrationResponse(
            id=registration.id,
            event_id=registration.event_id,
            username=registration.username,
            registered_at=registration.registered_at,
            is_active=registration.is_active
        )