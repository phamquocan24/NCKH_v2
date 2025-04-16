# api/routes/prediction.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from backend.db.models import get_db, Comment, User
from backend.api.models.prediction import PredictionRequest, PredictionResponse, BatchPredictionRequest, BatchPredictionResponse
from backend.services.ml_model import MLModel
from backend.api.routes.auth import get_current_user
from backend.utils.vector_utils import extract_features
import numpy as np

router = APIRouter()
ml_model = MLModel()

@router.post("/single", response_model=PredictionResponse)
async def predict_single(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Make prediction
    prediction, confidence = ml_model.predict(request.text)
    
    # Map prediction to text
    prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
    
    # Store prediction in background
    background_tasks.add_task(
        store_prediction, 
        db=db, 
        content=request.text, 
        platform=request.platform, 
        platform_id=request.platform_id, 
        prediction=prediction, 
        confidence=confidence, 
        user_id=current_user.id,
        metadata=request.metadata
    )
    
    return {
        "text": request.text,
        "prediction": prediction,
        "confidence": confidence,
        "prediction_text": prediction_text
    }

@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = []
    
    for comment in request.comments:
        prediction, confidence = ml_model.predict(comment.text)
        prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
        
        # Store prediction in background
        background_tasks.add_task(
            store_prediction, 
            db=db, 
            content=comment.text, 
            platform=comment.platform, 
            platform_id=comment.platform_id, 
            prediction=prediction, 
            confidence=confidence, 
            user_id=current_user.id,
            metadata=comment.metadata
        )
        
        results.append({
            "text": comment.text,
            "prediction": prediction,
            "confidence": confidence,
            "prediction_text": prediction_text
        })
    
    return {"results": results}

def store_prediction(
    db: Session, 
    content: str, 
    platform: str, 
    platform_id: str, 
    prediction: int, 
    confidence: float, 
    user_id: int,
    metadata: dict = None
):
    # Extract vector features
    vector = extract_features(content)
    
    # Create comment
    comment = Comment(
        content=content,
        platform=platform,
        platform_id=platform_id,
        prediction=prediction,
        confidence=confidence,
        user_id=user_id,
        metadata=metadata
    )
    
    # Set vector
    comment.set_vector(vector)
    
    # Store in database
    db.add(comment)
    db.commit()