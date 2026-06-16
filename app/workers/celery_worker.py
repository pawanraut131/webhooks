from celery import Celery
import time
from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import WebhookEvent

# Initialize the Celery app
# The first argument 'worker' is the name of the current module.
# broker=settings.REDIS_URL tells Celery to use our local Redis instance as the message broker.
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL # Store results in Redis too (optional but good practice)
)

@celery_app.task(name="process_github_webhook")
def process_webhook_task(delivery_id: str):
    """
    This is the background task that processes the webhook event asynchronously.
    It takes the delivery_id, looks up the event in the database, and processes it.
    
    Args:
        delivery_id: The unique ID of the webhook event.
    """
    print(f"[{delivery_id}] Starting background processing...")
    
    # Create a new database session for this worker task
    db = SessionLocal()
    try:
        # 1. Fetch the event from the database using the delivery_id
        # We use .first() to get the first matching record (it should be unique anyway)
        event = db.query(WebhookEvent).filter(WebhookEvent.delivery_id == delivery_id).first()
        
        if not event:
            print(f"[{delivery_id}] Error: Event not found in database!")
            return
            
        if event.processed:
            print(f"[{delivery_id}] Event already marked as processed.")
            return

        # 2. Simulate some heavy processing work
        # In a real app, you might parse the event.payload (which is JSON string),
        # extract commit data, send Slack notifications, update analytics dashboards, etc.
        print(f"[{delivery_id}] Parsing payload for event type: {event.event_type} on repo: {event.repository_name}")
        
        # Simulating time-consuming task (e.g., calling another API, analyzing code)
        time.sleep(3) 
        
        # 3. Mark the event as processed in the database
        event.processed = True
        db.commit() # Save the changes to the database
        
        print(f"[{delivery_id}] Successfully processed and updated database.")
        
    except Exception as e:
        print(f"[{delivery_id}] An error occurred during processing: {e}")
        # In a real production app, you might want to log this error to Sentry or a log file,
        # and possibly retry the task if it's a transient error.
    finally:
        # Always make sure to close the database session when the task is done
        db.close()
