import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

class Settings:
    """Centralized configuration for the TrustLayer Engine."""
    PROJECT_NAME: str = "TrustLayer Engine"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security & API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ENV: str = os.getenv("ENV", "development")

# Create a single instance to be imported across the application
settings = Settings()