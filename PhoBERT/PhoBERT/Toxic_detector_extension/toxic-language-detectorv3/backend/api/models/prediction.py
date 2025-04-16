# api/models/prediction.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    platform: str
    platform_id: str
    metadata: Optional[Dict[str, Any]] = None

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    prediction: int
    confidence: float
    created_at: datetime
    
    class Config:
        orm_mode = True

class PredictionRequest(BaseModel):
    text: str
    platform: Optional[str] = "unknown"
    platform_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    text: str
    prediction: int = Field(..., description="0: clean, 1: offensive, 2: hate, 3: spam")
    confidence: float
    prediction_text: str
    
    class Config:
        schema_extra = {
            "example": {
                "text": "This is a sample comment",
                "prediction": 0,
                "confidence": 0.95,
                "prediction_text": "clean"
            }
        }

class BatchPredictionRequest(BaseModel):
    comments: List[PredictionRequest]

class BatchPredictionResponse(BaseModel):
    results: List[PredictionResponse]
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class LogResponse(BaseModel):
    id: int
    request_path: str
    request_method: str
    response_status: int
    timestamp: datetime
    client_ip: str
    
    class Config:
        orm_mode = True