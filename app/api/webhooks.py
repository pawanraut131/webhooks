from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import WebhookEvent
from app.core.config import settings
from app.core.security import verify_github_signature
from app.workers.celery_worker import process_webhook_task
import json

# Create an APIRouter instance to group webhook-related endpoints
router = APIRouter()

@router.post("/github")
async def receive_github_webhook(
    request: Request,
    x_github_event: str = Header(None, description="The type of GitHub event"),
    x_github_delivery: str = Header(None, description="Unique ID for the delivery"),
    x_hub_signature_256: str = Header(None, description="HMAC SHA256 signature from GitHub"),
    db: Session = Depends(get_db)
):
    """
    Endpoint to receive webhooks from GitHub.
    It follows the "Fast Response" pattern: 
    Validate -> Save to DB -> Queue Task -> Return 200 OK immediately.
    """
    # 1. Read the raw request body. 
    # We need the raw bytes to verify the HMAC signature correctly.
    payload_body = await request.body()
    
    # 2. Verify the Signature (Security)
    # This ensures the request actually came from GitHub and has the correct secret.
    # If the signature is invalid, verify_github_signature will raise an HTTPException (401).
    verify_github_signature(settings.GITHUB_WEBHOOK_SECRET, payload_body, x_hub_signature_256)
    
    # Check if necessary headers are present
    if not x_github_event or not x_github_delivery:
        raise HTTPException(status_code=400, detail="Missing required GitHub headers.")

    # 3. Parse the payload JSON string into a Python dictionary to extract some basic info
    try:
        payload_data = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    # Try to extract the repository name safely
    repo_name = payload_data.get("repository", {}).get("name", "unknown_repo")

    # 4. Idempotency Check
    # Have we seen this exact delivery_id before?
    existing_event = db.query(WebhookEvent).filter(WebhookEvent.delivery_id == x_github_delivery).first()
    if existing_event:
        # If we already have it, GitHub might be retrying. 
        # We just return 200 OK to stop them from retrying, and ignore the duplicate.
        return {"message": "Event already received and processing/processed.", "delivery_id": x_github_delivery}

    # 5. Save the event to the Database (Persistence)
    # This guarantees we never lose an event even if the background worker crashes.
    new_event = WebhookEvent(
        delivery_id=x_github_delivery,
        event_type=x_github_event,
        repository_name=repo_name,
        # Save the raw payload body as text
        payload=payload_body.decode('utf-8')
    )
    
    db.add(new_event)
    db.commit()
    # No need to refresh the object from DB unless we need its auto-generated ID, 
    # but we will just pass the delivery_id to the worker.

    # 6. Queue the Background Task (Speed)
    # We use .delay() to tell Celery to run this function asynchronously in the background.
    process_webhook_task.delay(x_github_delivery)

    # 7. Respond to GitHub quickly!
    return {"message": "Webhook received successfully", "delivery_id": x_github_delivery}
