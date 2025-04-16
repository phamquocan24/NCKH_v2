# api/routes/toxic_detection.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.db.models import get_db, Comment
from backend.api.models.prediction import CommentResponse
from backend.api.routes.auth import get_current_user
from backend.db.models import User
from backend.utils.vector_utils import compute_similarity, extract_features
import numpy as np

router = APIRouter()

@router.get("/similar", response_model=List[CommentResponse])
def find_similar_comments(
    text: str,
    limit: int = 10,
    threshold: float = 0.7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Extract features for the query text
    query_vector = extract_features(text)
    
    # Get all comments from the database
    comments = db.query(Comment).all()
    
    # Compute similarity
    similar_comments = []
    for comment in comments:
        comment_vector = comment.get_vector()
        if comment_vector is not None:
            similarity = compute_similarity(query_vector, comment_vector)
            if similarity >= threshold:
                similar_comments.append((comment, similarity))
    
    # Sort by similarity (descending)
    similar_comments.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N comments
    return [comment for comment, _ in similar_comments[:limit]]

@router.get("/statistics")
def get_statistics(
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Comment)
    
    if platform:
        query = query.filter(Comment.platform == platform)
    
    total = query.count()
    clean = query.filter(Comment.prediction == 0).count()
    offensive = query.filter(Comment.prediction == 1).count()
    hate = query.filter(Comment.prediction == 2).count()
    spam = query.filter(Comment.prediction == 3).count()
    
    return {
        "total": total,
        "clean": clean,
        "offensive": offensive,
        "hate": hate,
        "spam": spam,
        "clean_percentage": (clean / total * 100) if total > 0 else 0,
        "offensive_percentage": (offensive / total * 100) if total > 0 else 0,
        "hate_percentage": (hate / total * 100) if total > 0 else 0,
        "spam_percentage": (spam / total * 100) if total > 0 else 0,
    }