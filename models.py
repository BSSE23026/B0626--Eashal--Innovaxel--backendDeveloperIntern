from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import declarative_base, relationship

# Create declarative base for all models
Base = declarative_base()


class Event(Base):
    """
    Event model representing an event that users can register for.
    
    Attributes:
        id: Primary key, auto-incremented integer
        name: Unique event name
        total_seats: Total number of available seats
        event_date: Date and time of the event (must be in future)
        created_at: Timestamp when event was created
        registrations: Relationship to Registration objects
    """
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    total_seats = Column(Integer, nullable=False)
    event_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to registrations
    registrations = relationship(
        "Registration",
        back_populates="event",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, name='{self.name}', total_seats={self.total_seats})>"


class Registration(Base):
    """
    Registration model representing a user's registration for an event.
    
    Attributes:
        id: Primary key, auto-incremented integer
        event_id: Foreign key to Event
        username: Name of the user registering
        registered_at: Timestamp when registration was made
        is_active: Flag to track if registration is cancelled
        event: Relationship to Event object
    """
    __tablename__ = "registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(255), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = cancelled
    
    # Relationship to event
    event = relationship("Event", back_populates="registrations")
    
    # Unique constraint: same user cannot register twice for the same event
    # We only count active registrations in this constraint
    __table_args__ = (
        UniqueConstraint("event_id", "username", name="unique_active_registration"),
        Index("idx_event_active", "event_id", "is_active"),
        Index("idx_username", "username"),
    )
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "cancelled"
        return f"<Registration(id={self.id}, event_id={self.event_id}, username='{self.username}', status='{status}')>"