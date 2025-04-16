# core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from backend.config.settings import settings
from typing import Optional
from backend.db.models import User

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# API key header for extension
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain password matches the hashed password
    
    Args:
        plain_password (str): Plain text password
        hashed_password (str): Hashed password
        
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta], optional): Token expiration time. Defaults to None.
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Verify API key for extension
    
    Args:
        api_key (str, optional): API key. Defaults to Depends(api_key_header).
        
    Raises:
        HTTPException: If the API key is invalid
        
    Returns:
        str: Verified API key
    """
    if api_key != settings.EXTENSION_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key