# api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.db.models import get_db, User, Role, Log, Comment
from backend.api.models.prediction import UserResponse, LogResponse, CommentResponse
from backend.api.routes.auth import get_admin_user

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

@router.get("/logs", response_model=List[LogResponse])
def get_logs(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    logs = db.query(Log).order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/comments", response_model=List[CommentResponse])
def get_comments(
    skip: int = 0, 
    limit: int = 100, 
    platform: str = None,
    prediction: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    query = db.query(Comment)
    
    if platform:
        query = query.filter(Comment.platform == platform)
    
    if prediction is not None:
        query = query.filter(Comment.prediction == prediction)
    
    comments = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    return comments