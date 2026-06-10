from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from pydantic import BaseModel
from database import Base

class User(Base):
    __tablename__ = "user"
    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    bio = Column(String, nullable=True)
    phone = Column(String, nullable=True)

class Blogs(Base):
    __tablename__ = "blogs"
    id           = Column(Integer, primary_key=True, index=True)
    userid       = Column(Integer, ForeignKey("user.id"), nullable=False)
    post         = Column(String, nullable=False)
    descriptions = Column(String, nullable=False)
    create_date  = Column(DateTime, default=datetime.now)

class BlogCreate(BaseModel):
    userid: int
    post: str
    descriptions: str