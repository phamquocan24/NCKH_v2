# db/models/role.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from backend.db.models.base import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    
    # Relationships
    users = relationship("User", back_populates="role")