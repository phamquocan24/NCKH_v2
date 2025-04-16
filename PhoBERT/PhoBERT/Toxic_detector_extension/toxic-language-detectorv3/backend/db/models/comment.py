# db/models/comment.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.models.base import Base
import numpy as np
import json

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    platform = Column(String, nullable=False)  # e.g. "facebook", "youtube", "twitter"
    platform_id = Column(String, index=True)  # Original ID from the platform
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Classification results
    prediction = Column(Integer)  # 0: clean, 1: offensive, 2: hate, 3: spam
    confidence = Column(Float)
    
    # Vector representation for similarity search
    vector_representation = Column(String)  # Stored as JSON string
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="comments")
    
    # Additional comment_metadata from the platform
    comment_metadata = Column(JSON)
    
    def set_vector(self, vector):
        """Convert numpy array to JSON string for storage"""
        if isinstance(vector, np.ndarray):
            self.vector_representation = json.dumps(vector.tolist())
        else:
            self.vector_representation = json.dumps(vector)
    
    def get_vector(self):
        """Get vector as numpy array"""
        if self.vector_representation:
            return np.array(json.loads(self.vector_representation))
        return None