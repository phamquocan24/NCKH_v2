# db/models/__init__.py
from backend.db.models.base import Base, engine, SessionLocal
from backend.db.models.user import User
from backend.db.models.role import Role
from backend.db.models.comment import Comment
from backend.db.models.log import Log

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()