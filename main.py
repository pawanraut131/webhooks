from fastapi import FastAPI
from app.api.webhooks import router as webhooks_router

# Initialize the FastAPI application
# We can add metadata here like title and description
app = FastAPI(
    title="GitHub Webhooks API",
    description="A learning project to handle GitHub webhooks in a production-like way.",
    version="1.0.0"
)

# Include the webhooks router
# This mounts our /github endpoint under the /webhooks prefix
# So the final URL will be: POST /webhooks/github
app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/")
def root():
    """
    A simple health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "GitHub Webhooks API is running!"}
