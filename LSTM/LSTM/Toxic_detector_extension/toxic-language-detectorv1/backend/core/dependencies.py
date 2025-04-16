# core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.db.models import get_db, User
from backend.config.settings import settings
from datetime import datetime, timedelta
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new JWT access token
    
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

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the current authenticated user
    
    Args:
        token (str, optional): JWT token. Defaults to Depends(oauth2_scheme).
        db (Session, optional): Database session. Defaults to Depends(get_db).
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
        
    Returns:
        User: Authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Get the current active user
    
    Args:
        current_user (User, optional): Current user. Defaults to Depends(get_current_user).
        
    Raises:
        HTTPException: If the user is inactive
        
    Returns:
        User: Active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Get the current admin user
    
    Args:
        current_user (User, optional): Current user. Defaults to Depends(get_current_user).
        
    Raises:
        HTTPException: If the user is not an admin
        
    Returns:
        User: Admin user
    """
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user