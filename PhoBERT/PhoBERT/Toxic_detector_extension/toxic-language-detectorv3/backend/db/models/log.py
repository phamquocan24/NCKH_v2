# db/models/log.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.models.base import Base

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_path = Column(String)
    request_method = Column(String)
    request_body = Column(Text, nullable=True)
    response_status = Column(Integer)
    response_body = Column(Text, nullable=True)
    client_ip = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # If request was authenticated, store user info
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Additional log_metadata
    log_metadata = Column(JSON, nullable=True)