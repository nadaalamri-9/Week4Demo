from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-many: a single User can have many Post objects.
    # Access in Python: user.posts -> list[Post]
    # The foreign key lives on Post (Post.user_id = users.id).
    posts = relationship("Post", back_populates="author")

    # One-to-one: a User has at most one UserProfile.
    # `uselist=False` makes `user.profile` return a single object, not a list.
    # Enforced at the DB level by making UserProfile.user_id unique.
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} active={self.is_active}>"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    body = Column(Text)
    is_published = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post id={self.id} title={self.title!r} user_id={self.user_id}>"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    bio = Column(Text)
    website = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile id={self.id} user_id={self.user_id}>"
