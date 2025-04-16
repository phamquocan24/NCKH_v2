# api/routes/extension.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.db.models import get_db, Comment
from backend.api.models.prediction import PredictionRequest, PredictionResponse
from backend.services.ml_model import MLModel
from backend.config.security import verify_api_key
from backend.utils.vector_utils import extract_features

router = APIRouter()
ml_model = MLModel()

@router.post("/detect", response_model=PredictionResponse)
async def extension_detect(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    # Make prediction
    prediction, confidence = ml_model.predict(request.text)
    
    # Map prediction to text
    prediction_text = {0: "clean", 1: "offensive", 2: "hate", 3: "spam"}[prediction]
    
    # Store prediction in background, but without user_id since this is from extension
    background_tasks.add_task(
        store_extension_prediction, 
        db=db, 
        content=request.text, 
        platform=request.platform, 
        platform_id=request.platform_id, 
        prediction=prediction, 
        confidence=confidence,
        metadata=request.metadata
    )
    
    return {
        "text": request.text,
        "prediction": prediction,
        "confidence": confidence,
        "prediction_text": prediction_text
    }

def store_extension_prediction(
    db: Session, 
    content: str, 
    platform: str, 
    platform_id: str, 
    prediction: int, 
    confidence: float,
    metadata: Dict[str, Any] = None
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
        user_id=None,  # No user associated with extension predictions
        metadata=metadata
    )
    
    # Set vector
    comment.set_vector(vector)
    
    # Store in database
    db.add(comment)
    db.commit()
