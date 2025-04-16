# config/settings.py
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API settings
    PROJECT_NAME: str = "Toxic Language Detector"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Extension API key
    EXTENSION_API_KEY: str = os.getenv("EXTENSION_API_KEY", "extension-api-key")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./toxic_detector.db")
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",  # Frontend development
        "http://localhost:8000",  # Backend development
        "chrome-extension://*",   # Chrome extension
    ]
    
    # ML Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "model/best_model_LSTM.h5")
    
    # Hugging Face settings
    HUGGINGFACE_API_URL: str = os.getenv("HUGGINGFACE_API_URL", "https://api-inference.huggingface.co/models/")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Social Media API settings
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()