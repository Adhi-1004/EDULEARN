"""
Application configuration settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    app_name: str = "eduLearn API"
    app_description: str = "AI-powered Adaptive Learning Platform API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/edulearn")
    db_name: str = os.getenv("DB_NAME", "edulearn")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://modlrn.vercel.app",
        "https://modlrn.onrender.com",
        "https://accounts.google.com",
        "https://oauth2.googleapis.com",
    ]

    # AI Services
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "AIzaSyCeT9KMPDDZwHFabO_57mx12SM27pDurh0")

    # Google OAuth
    google_client_id: str = os.getenv(
        "GOOGLE_CLIENT_ID",
        "390673176588-srmffm0pi2t4u4qs4o7kdelh72vj47fq.apps.googleusercontent.com",
    )
    google_client_secret: str = os.getenv(
        "GOOGLE_CLIENT_SECRET", "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"
    )

    # Code Execution
    code_execution_timeout: int = 5
    code_memory_limit: int = 256

    # Judge0 API
    judge0_api_key: str = os.getenv("JUDGE0_API_KEY", "")
    judge0_api_host: str = os.getenv("JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")

    # Session
    session_secret: str = os.getenv(
        "SESSION_SECRET", "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"
    )


settings = Settings()
