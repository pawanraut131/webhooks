from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class WebhookEvent(Base):
    """
    SQLAlchemy model representing the 'webhook_events' table in PostgreSQL.
    This table stores every webhook we receive so we never lose an event.
    """
    __tablename__ = "webhook_events"

    # The primary key for the database row
    id = Column(Integer, primary_key=True, index=True)
    
    # The unique delivery ID sent by GitHub (X-GitHub-Delivery header).
    # We use this for idempotency to ensure we don't process the same event twice.
    # Marking it as unique=True enforces this constraint at the database level.
    delivery_id = Column(String, unique=True, index=True, nullable=False)
    
    # The type of the event (e.g., 'push', 'pull_request', 'issues')
    event_type = Column(String, nullable=False)
    
    # The name of the repository the event came from
    repository_name = Column(String, nullable=False)
    
    # The raw JSON payload from GitHub, stored as Text.
    # In PostgreSQL, this could also be JSONB for better query performance,
    # but Text works well for a learning project.
    payload = Column(Text, nullable=False)
    
    # A flag to track if the background worker has finished processing this event
    processed = Column(Boolean, default=False)
    
    # A timestamp for when the event was received and stored
    created_at = Column(DateTime(timezone=True), server_default=func.now())
