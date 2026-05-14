from datetime import *

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    city = Column(String, index=True)
    country = Column(String)
    location = Column(String)
    role = Column(String, default="users")
    profile_picture = Column(String, nullable=True)
    tasks = relationship("Tasks", back_populates="owner", cascade="all, delete")


class UserLogs(Base):
    __tablename__ = 'userlogs'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    ip = Column(String)
    location = Column(String, nullable=True)
    activity = Column(String)
    activity_time = Column(DateTime, default=datetime.now(timezone.utc))


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String)
    description = Column(String, default=None, nullable=True)
    completed = Column(String, default="no")
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=None)
    deleted = Column(Boolean, default=False)
    owner = relationship("Users", back_populates="tasks")
