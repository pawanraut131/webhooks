import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Settings class to manage application configuration.
    It reads variables from the environment or the .env file.
    """
    # The URL to connect to the PostgreSQL database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/newdb")
    
    # The URL to connect to the Redis server for Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # The secret key used to verify incoming GitHub webhook signatures
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "super-secret-key")

# Instantiate the settings object so it can be imported across the app
settings = Settings()
