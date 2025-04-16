# services/user_service.py
from sqlalchemy.orm import Session
from backend.db.models import User, Role
from backend.core.security import get_password_hash, verify_password
from typing import Optional, List

class UserService:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get a user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, role_name: str = "user") -> User:
        """Create a new user"""
        # Get role
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name.capitalize()} role")
            db.add(role)
            db.commit()
            db.refresh(role)
        
        # Create user
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role_id=role.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = UserService.get_user_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """Update user details"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        for key, value in kwargs.items():
            if key == "password":
                value = get_password_hash(value)
                key = "hashed_password"
            
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user