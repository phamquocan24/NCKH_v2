# config/security.py
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from backend.config.settings import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API key for extension
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate password hash"""
    return pwd_context.hash(password)

def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key for extension"""
    if api_key != settings.EXTENSION_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )