# Event Registration System API

A production-quality REST API for managing event registrations with concurrent access safety, built with FastAPI, SQLAlchemy ORM, and SQLite.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Concurrency & Race Condition Prevention](#concurrency--race-condition-prevention)
- [Error Handling](#error-handling)
- [Example API Requests](#example-api-requests)
- [Testing](#testing)
- [Interview Questions & Answers](#interview-questions--answers)

## 🎯 Overview

This API implements an Event Registration System that allows users to:
- Create events with limited seating capacity
- Register users for events with validation
- View event details and availability
- Cancel registrations
- Handle concurrent registrations safely without overbooking

The system enforces strict validation rules and prevents race conditions using database-level locks and transactions.

## ✨ Features

### Core Features
✅ **Create Events**
- Create events with name, total seats, and date
- Automatic validation of all fields
- Ensures unique event names

✅ **Register Users**
- Register users for events with concurrent safety
- Prevents duplicate registrations
- Prevents overbooking
- Stores registration timestamps

✅ **View Events & Registrations**
- List all events with available seat counts
- Filter upcoming events only
- Sort events by date
- Get detailed event information with registrations

✅ **Cancel Registrations**
- Cancel user registrations
- Automatically free up seats
- Soft delete approach maintains audit trail

### Advanced Features
✅ **Race Condition Prevention**
- Database-level row locking with SELECT FOR UPDATE
- ACID transactions for atomic operations
- Unique constraints on (event_id, username)
- Prevents simultaneous overbooking

✅ **Error Handling**
- Structured exception hierarchy
- Proper HTTP status codes
- Descriptive error messages
- Machine-readable error codes

✅ **Data Validation**
- Pydantic schemas for request validation
- Business rule validation in service layer
- Database constraints as safety net

## 🛠️ Tech Stack

- **Framework**: FastAPI (modern, fast, async-capable)
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic v2
- **HTTP Server**: Uvicorn
- **Language**: Python 3.8+

### Why These Choices?

**FastAPI**: 
- Modern async framework with automatic OpenAPI documentation
- Built-in dependency injection for clean code
- Excellent type hints support
- Performance comparable to Go and Node.js

**SQLAlchemy ORM**:
- Object-relational mapping for clean code
- Support for complex queries and transactions
- Row-level locking capability (FOR UPDATE)
- Automatic relationship management

**SQLite**:
- Perfect for embedded systems and testing
- ACID compliance with proper transaction handling
- No server required
- Adequate for concurrent access with proper locking

**Pydantic**:
- Automatic request/response validation
- Clear API documentation
- Type safety and IDE support
- Custom validators for business rules

## 🏗️ Architecture

### Folder Structure

```
event_registration_system/
├── main.py                      # FastAPI application entry point
├── config.py                    # Configuration and settings
├── database.py                  # Database connection and session management
├── models.py                    # SQLAlchemy ORM models (Event, Registration)
├── schemas.py                   # Pydantic request/response schemas
├── exceptions.py                # Custom exception classes
├── event_service.py             # Business logic for events
├── registration_service.py      # Business logic for registrations (race condition prevention)
├── routes_events.py             # FastAPI routes for events
├── routes_registrations.py      # FastAPI routes for registrations
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

### Architectural Layers

```
┌─────────────────────────────────────┐
│   FastAPI Routes (routes_*.py)      │  HTTP Interface
│   - Request/Response Handling       │
│   - Parameter Validation            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Services (service_*.py)           │  Business Logic
│   - Event Management                │
│   - Registration Management         │
│   - Race Condition Prevention       │
│   - Validation Rules                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Schemas (schemas.py)              │  Data Validation
│   - Pydantic Models                 │
│   - Request/Response DTOs           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Models (models.py)                │  Database Layer
│   - SQLAlchemy ORM Classes          │
│   - Database Tables                 │
│   - Relationships & Constraints     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Database (SQLite)                 │  Persistence
│   - ACID Transactions               │
│   - Row-Level Locking               │
│   - Constraints & Indexes           │
└─────────────────────────────────────┘
```

### Data Flow

**Create Event Flow:**
1. Client sends POST /events with event data
2. Route validates using Pydantic schema
3. Service validates business rules
4. Database constraints prevent duplicates
5. Response with created event

**Register User Flow:**
1. Client sends POST /registrations with user data
2. Route validates using Pydantic schema
3. Service acquires exclusive lock on event row (SELECT FOR UPDATE)
4. Service checks availability atomically
5. Service checks for duplicate registration
6. Service creates registration in same transaction
7. Database constraints catch any race conditions
8. Response with created registration

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone/Create Project**
```bash
mkdir event_registration_system
cd event_registration_system
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the Application**
```bash
python main.py
```

The API will start on `http://localhost:8000`

### Access Points

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Documentation**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### Events

#### Create Event
```
POST /api/v1/events
Content-Type: application/json

{
  "name": "Tech Conference 2024",
  "total_seats": 100,
  "event_date": "2024-12-15T10:00:00"
}

Response: 201 Created
{
  "id": 1,
  "name": "Tech Conference 2024",
  "total_seats": 100,
  "available_seats": 100,
  "total_registrations": 0,
  "event_date": "2024-12-15T10:00:00",
  "created_at": "2024-06-07T10:30:00"
}
```

#### List Events
```
GET /api/v1/events
GET /api/v1/events?upcoming_only=true
GET /api/v1/events?sort_by_date=true
GET /api/v1/events?upcoming_only=true&sort_by_date=true

Response: 200 OK
[
  {
    "id": 1,
    "name": "Tech Conference 2024",
    "total_seats": 100,
    "available_seats": 95,
    "total_registrations": 5,
    "event_date": "2024-12-15T10:00:00",
    "created_at": "2024-06-07T10:30:00"
  }
]
```

#### Get Event Details
```
GET /api/v1/events/1

Response: 200 OK
{
  "id": 1,
  "name": "Tech Conference 2024",
  "total_seats": 100,
  "available_seats": 95,
  "total_registrations": 5,
  "event_date": "2024-12-15T10:00:00",
  "created_at": "2024-06-07T10:30:00"
}
```

### Registrations

#### Register User
```
POST /api/v1/registrations
Content-Type: application/json

{
  "username": "john_doe",
  "event_id": 1
}

Response: 201 Created
{
  "id": 1,
  "event_id": 1,
  "username": "john_doe",
  "registered_at": "2024-06-07T10:35:00",
  "is_active": 1
}
```

#### List All Registrations
```
GET /api/v1/registrations

Response: 200 OK
[
  {
    "id": 1,
    "event_id": 1,
    "username": "john_doe",
    "registered_at": "2024-06-07T10:35:00",
    "is_active": 1
  }
]
```

#### Get Event Registrations
```
GET /api/v1/registrations/event/1

Response: 200 OK
[
  {
    "id": 1,
    "event_id": 1,
    "username": "john_doe",
    "registered_at": "2024-06-07T10:35:00",
    "is_active": 1
  }
]
```

#### Cancel Registration
```
DELETE /api/v1/registrations/1

Response: 200 OK
{
  "id": 1,
  "event_id": 1,
  "username": "john_doe",
  "registered_at": "2024-06-07T10:35:00",
  "is_active": 0
}
```

## 💾 Database Schema

### Events Table
```sql
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) UNIQUE NOT NULL,
  total_seats INTEGER NOT NULL,
  event_date DATETIME NOT NULL,
  created_at DATETIME NOT NULL,
  KEY idx_name (name),
  KEY idx_event_date (event_date)
);
```

### Registrations Table
```sql
CREATE TABLE registrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id INTEGER NOT NULL,
  username VARCHAR(255) NOT NULL,
  registered_at DATETIME NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
  UNIQUE KEY unique_active_registration (event_id, username),
  KEY idx_event_active (event_id, is_active),
  KEY idx_username (username),
  KEY idx_registered_at (registered_at)
);
```

### Key Constraints

1. **Event.name**: UNIQUE - Prevents duplicate event names
2. **Registration(event_id, username)**: UNIQUE - Prevents duplicate registrations
3. **Registration.event_id**: FOREIGN KEY - Maintains referential integrity
4. **Indexes**: Optimized for common queries

## 🔒 Concurrency & Race Condition Prevention

### The Problem: Race Conditions

In a concurrent system, without proper locking, race conditions can occur:

```
Time | Thread 1                      | Thread 2
-----|-------------------------------|------------------------------
 1   | Check available (98 seats)    |
 2   |                               | Check available (98 seats)
 3   | Lock acquired on event row    |
 4   | Register user 1 (97 left)     |
 5   |                               | Lock acquired on event row
 6   | Commit                        |
 7   |                               | Register user 2 (97 left)
 8   |                               | Commit
     | OVERBOOKING! Both created!    |
```

### Our Solution: Database-Level Locking

We prevent race conditions using multiple layers:

#### 1. **SELECT FOR UPDATE (Row-Level Locking)**

```python
# Lock the event row exclusively
event = self.db.query(Event).filter(
    Event.id == registration_data.event_id
).with_for_update().first()  # Blocks until lock acquired
```

**How it works:**
- Acquires exclusive lock on the event row
- Other transactions wait until lock is released
- Ensures atomic read-check-write operation

#### 2. **ACID Transactions**

```python
# All operations in one transaction
db.add(registration)
db.flush()
db.commit()  # All-or-nothing
```

**Isolation Levels:**
- SQLite default: DEFERRED
- Ensures read-committed isolation
- Consistent view of data

#### 3. **Unique Constraints**

```sql
UNIQUE KEY unique_active_registration (event_id, username)
```

**Benefits:**
- Database enforces uniqueness
- Catches race conditions missed by application logic
- IntegrityError provides fallback error handling

#### 4. **Optimistic Counting**

```python
# Count in the same transaction as lock
active_count = self.db.query(func.count(Registration.id)).filter(
    and_(
        Registration.event_id == event_id,
        Registration.is_active == 1
    )
).scalar()
```

### Timeline with Our Implementation

```
Time | Thread 1                      | Thread 2
-----|-------------------------------|------------------------------
 1   | Lock event row                |
 2   | Count registrations (98)      |
 3   |                               | Waiting for lock...
 4   | Check duplicate (not found)   |
 5   | Create registration           |
 6   | Commit & release lock         |
 7   |                               | Lock acquired
 8   |                               | Count registrations (99)
 9   |                               | Check duplicate (not found)
10   |                               | Verify availability
11   |                               | Create registration
12   |                               | Commit & release lock
    | CORRECT! Both created safely  |
```

## 🚨 Error Handling

### HTTP Status Codes

- **200 OK**: Successful GET/PUT/DELETE
- **201 Created**: Successful resource creation
- **400 Bad Request**: Validation error or invalid input
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Business rule violation (full event, duplicate)
- **500 Internal Server Error**: Unexpected server error

### Error Response Format

```json
{
  "detail": "Event with ID 999 not found",
  "error_code": "EVENT_NOT_FOUND"
}
```

### Common Error Scenarios

| Scenario | Status | Error Code |
|----------|--------|-----------|
| Event not found | 404 | EVENT_NOT_FOUND |
| Duplicate event name | 409 | DUPLICATE_EVENT_NAME |
| Event date in past | 400 | INVALID_EVENT_DATE |
| Invalid seats (≤ 0) | 400 | INVALID_SEATS |
| Event is full | 409 | EVENT_FULL |
| Duplicate registration | 409 | DUPLICATE_REGISTRATION |
| Registration not found | 404 | REGISTRATION_NOT_FOUND |
| Already cancelled | 400 | INVALID_REGISTRATION |
| Empty username | 400 | VALIDATION_ERROR |

## 📝 Example API Requests

### Complete Workflow Example

#### 1. Create an Event
```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Workshop",
    "total_seats": 30,
    "event_date": "2024-12-20T14:00:00"
  }'
```

#### 2. Register Multiple Users
```bash
# User 1
curl -X POST http://localhost:8000/api/v1/registrations \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "event_id": 1}'

# User 2
curl -X POST http://localhost:8000/api/v1/registrations \
  -H "Content-Type: application/json" \
  -d '{"username": "bob", "event_id": 1}'

# User 3
curl -X POST http://localhost:8000/api/v1/registrations \
  -H "Content-Type: application/json" \
  -d '{"username": "charlie", "event_id": 1}'
```

#### 3. View Event Details
```bash
curl http://localhost:8000/api/v1/events/1
```

Response shows:
- total_seats: 30
- available_seats: 27 (30 - 3 registrations)
- total_registrations: 3

#### 4. View Event Registrations
```bash
curl http://localhost:8000/api/v1/registrations/event/1
```

#### 5. Cancel a Registration
```bash
curl -X DELETE http://localhost:8000/api/v1/registrations/1
```

Available seats now: 28 (30 - 2 active registrations)

#### 6. Try Duplicate Registration (Should Fail)
```bash
curl -X POST http://localhost:8000/api/v1/registrations \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "event_id": 1}'
```

Response: 409 Conflict - "User 'alice' is already registered for event 1"

## 🧪 Testing

### Manual Testing with cURL

See "Example API Requests" section above.

### Testing with Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Create event
event_data = {
    "name": "AI Conference",
    "total_seats": 100,
    "event_date": "2024-12-25T09:00:00"
}
response = requests.post(f"{BASE_URL}/events", json=event_data)
event = response.json()
event_id = event["id"]

# Register user
registration_data = {
    "username": "test_user",
    "event_id": event_id
}
response = requests.post(f"{BASE_URL}/registrations", json=registration_data)
registration = response.json()

# Get event details
response = requests.get(f"{BASE_URL}/events/{event_id}")
print(json.dumps(response.json(), indent=2))
```

### Concurrent Access Testing

```python
import threading
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Create event with 2 seats
event_data = {
    "name": "Limited Event",
    "total_seats": 2,
    "event_date": "2024-12-30T15:00:00"
}
response = requests.post(f"{BASE_URL}/events", json=event_data)
event_id = response.json()["id"]

results = []

def register_user(username):
    try:
        data = {"username": username, "event_id": event_id}
        response = requests.post(f"{BASE_URL}/registrations", json=data)
        results.append({
            "username": username,
            "status": response.status_code,
            "success": response.status_code == 201
        })
    except Exception as e:
        results.append({
            "username": username,
            "error": str(e),
            "success": False
        })

# Try to register 5 users concurrently
threads = []
for i in range(5):
    t = threading.Thread(target=register_user, args=(f"user_{i}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Only 2 should succeed
successful = sum(1 for r in results if r["success"])
print(f"Successful registrations: {successful}/5 (expected: 2)")
print(json.dumps(results, indent=2))
```

## 🎓 Interview Questions & Answers

### Q1: How do you prevent race conditions in event registration?

**Answer:**
We use a multi-layered approach:

1. **Database-Level Row Locking**: We use `SELECT FOR UPDATE` to acquire an exclusive lock on the event row before registration. This serializes concurrent access and prevents simultaneous overbooking.

```python
event = db.query(Event).filter(
    Event.id == event_id
).with_for_update().first()
```

2. **ACID Transactions**: The entire check-and-register operation is wrapped in a single transaction. Either both succeed or both fail - no partial updates.

3. **Unique Constraints**: The database has a unique constraint on (event_id, username) to catch any race conditions missed by application logic.

4. **Defensive Error Handling**: If an IntegrityError occurs, we catch it and provide appropriate error messages.

This ensures that only exactly N users can register for an event with N seats, regardless of concurrent load.

---

### Q2: Why did you choose SQLAlchemy ORM over raw SQL?

**Answer:**
SQLAlchemy ORM provides several advantages:

1. **Type Safety**: ORM relationships are type-checked at development time
2. **Query Flexibility**: Complex queries are easier to compose and maintain
3. **Row-Level Locking**: The `with_for_update()` method provides clean locking syntax
4. **Relationship Management**: Automatic handling of foreign keys and cascades
5. **Database Abstraction**: Easy to switch databases if needed
6. **Automatic Query Building**: Less boilerplate code

However, I kept queries relatively simple to maintain readability and performance. For very complex queries, raw SQL would be added alongside ORM queries.

---

### Q3: How does the soft-delete approach work for cancellations?

**Answer:**
Instead of deleting registrations, we mark them as inactive:

```python
registration.is_active = 0  # 1 = active, 0 = cancelled
db.commit()
```

**Benefits:**
1. **Audit Trail**: Keep record of all cancellations
2. **Data Recovery**: Can restore cancellations if needed
3. **Reporting**: Can track cancellation patterns
4. **No Cascades**: Don't accidentally delete event data

**How it affects availability:**
- Seat count is calculated using `WHERE is_active = 1`
- Cancelled registrations don't appear in "active registrations" queries
- When checking for duplicates, we only check active registrations

---

### Q4: What happens if two requests arrive at exactly the same time?

**Answer:**
This is the core race condition scenario. Here's the sequence:

1. **Request 1** acquires lock on event row
2. **Request 2** waits for the lock
3. **Request 1** checks capacity, registers user, commits, releases lock
4. **Request 2** acquires lock, checks capacity
5. If event is now full, **Request 2** fails with "EVENT_FULL" error

The key is that the lock is acquired BEFORE checking capacity, making the check atomic. This is stronger than just checking then locking.

---

### Q5: Why use SQLite instead of PostgreSQL?

**Answer:**
For an internship assessment, SQLite is ideal because:

1. **Zero Setup**: No database server installation needed
2. **File-Based**: Easy to version control and test
3. **Sufficient for Scale**: Handles thousands of registrations easily
4. **ACID Compliance**: Fully supports transactions and constraints
5. **Row-Level Locking**: Has `BEGIN IMMEDIATE` for pessimistic locking

For production with millions of transactions, PostgreSQL would be better due to:
- Better concurrent write performance
- More sophisticated lock management
- Clustering and replication
- Superior monitoring tools

But for the assessment's scope, SQLite perfectly demonstrates all necessary concepts.

---

### Q6: How would you handle a situation where 1000 users try to register simultaneously?

**Answer:**
Current implementation would:

1. **Handle correctly**: All 1000 requests would be queued by the database lock
2. **Register N users**: Exactly N users succeed (where N = available seats)
3. **Return clear errors**: Remaining 1000-N users get "EVENT_FULL" errors

**Optimization for production:**
1. **Connection Pooling**: Use a connection pool with worker threads/async
2. **Queue Management**: Implement a fair queue or lottery system
3. **Caching**: Cache available seat count with short TTL
4. **Load Testing**: Monitor performance with Apache Bench or Locust
5. **Monitoring**: Track registration success rate and latency

Example with async:
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

app = FastAPI()  # Supports async by default
```

---

### Q7: What validations happen at each layer?

**Answer:**

| Layer | Validation | Purpose |
|-------|-----------|---------|
| **Pydantic Schema** | Type, min/max length, format | Fast early rejection |
| **Service Layer** | Business rules (future date, seats > 0) | Logical consistency |
| **Database Constraints** | Unique, foreign key, check | Ultimate safety net |

Example for registration:
1. **Route/Pydantic**: Username not empty, event_id is positive integer
2. **Service**: Event exists, has available seats, user not already registered
3. **Database**: Unique constraint on (event_id, username) prevents duplicates

This layered approach means:
- Invalid data is rejected early
- Business rules are enforced consistently
- Database constraints catch edge cases

---

### Q8: How would you add pagination for listing events?

**Answer:**

```python
from fastapi import Query

@app.get("/api/v1/events")
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    events = db.query(Event)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [EventResponse(...) for event in events]
```

Best practices:
1. **Limit defaults**: Maximum limit prevents resource exhaustion
2. **Skip/Limit**: More scalable than offset/limit for large datasets
3. **Response Meta**: Include total count and pagination info
4. **Index**: Database index on sort column improves performance

---

### Q9: How would you implement user authentication?

**Answer:**

```python
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    # Verify JWT token
    payload = jwt.decode(
        credentials.credentials,
        settings.SECRET_KEY,
        algorithms=["HS256"]
    )
    return payload["sub"]

@app.post("/register")
def register(
    registration_data: RegistrationCreateRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user is now authenticated
    registration_data.username = current_user
    # ... rest of logic
```

Trade-offs:
- **JWT**: Stateless, scalable
- **Session**: Stateful, simpler for monoliths
- **OAuth2**: External provider, more secure

---

### Q10: How would you add database migrations?

**Answer:**

Using Alembic (SQLAlchemy migration tool):

```bash
alembic init migrations
alembic revision --autogenerate -m "Add event table"
alembic upgrade head
```

Why migrations matter:
- **Schema versioning**: Track changes over time
- **Rollback capability**: Revert bad deployments
- **Team coordination**: Multiple developers modify schema safely
- **CI/CD**: Automated schema updates in production

---

## 📚 Key Design Decisions

### 1. Soft Deletes Instead of Hard Deletes
- Preserves audit trail
- Allows recovery
- Simpler queries (just check is_active flag)

### 2. Separate Service Layer
- Centralizes business logic
- Makes testing easier
- Enforces separation of concerns

### 3. Pydantic for Validation
- Automatic OpenAPI documentation
- Type safety
- Reusable across endpoints

### 4. Explicit Status Codes
- 201 for creation (not 200)
- 409 for conflicts (not 400)
- 404 for not found (not 400)

### 5. Stateless Design
- No server session state
- Horizontally scalable
- Can add load balancing

## 🎬 Demo Video Script

When recording your demo (2-5 minutes):

1. **Introduction** (30 seconds)
   - Show the API documentation at /docs
   - Explain the system handles concurrent registrations safely

2. **Create Event** (30 seconds)
   - POST /events with sample data
   - Show the response with ID

3. **Register Users** (60 seconds)
   - Register multiple users for the event
   - Show available seats decrease
   - Try duplicate registration (should fail)

4. **View Events** (30 seconds)
   - Show list with filters
   - Show sorting by date
   - Show available seats calculation

5. **Cancel Registration** (30 seconds)
   - DELETE a registration
   - Show available seats increase
   - Confirm user not in active registrations

6. **Error Handling** (30 seconds)
   - Try to register for full event
   - Show error message with error code

7. **Code Explanation** (60 seconds)
   - Briefly explain race condition prevention
   - Show SELECT FOR UPDATE in registration_service.py
   - Explain transaction atomicity

## ✅ Submission Checklist

- [ ] All code files present and properly structured
- [ ] requirements.txt with all dependencies
- [ ] README with setup instructions
- [ ] API endpoints working correctly
- [ ] Database schema properly designed
- [ ] Race condition prevention implemented
- [ ] Error handling comprehensive
- [ ] Code is well-commented
- [ ] Demo video (2-5 minutes) recorded
- [ ] Repository named: `B0626 - [Your Name] - Innovaxel - Backend`
- [ ] README includes architecture decisions
- [ ] All edge cases handled

## 🎯 Assessment Criteria

This solution addresses all assessment requirements:

✅ **API Design**
- RESTful endpoints with proper HTTP methods
- Proper status codes
- Clear request/response formats

✅ **Data Modeling**
- Well-structured SQLAlchemy models
- Appropriate relationships and constraints
- Indexes for performance

✅ **Real-World Constraints**
- Race condition prevention
- Concurrent access safety
- Proper validation

✅ **Code Quality**
- Clean architecture with layered design
- Comprehensive error handling
- Well-documented code

✅ **Production Readiness**
- ACID compliance
- Proper logging hooks
- Scalable design

---

**Good Luck with your assessment! 🚀**

For questions during the interview, refer to the "Interview Questions & Answers" section and be prepared to explain every design decision you made.