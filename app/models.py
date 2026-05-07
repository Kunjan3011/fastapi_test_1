from datetime import *

from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, DateTime, Boolean

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
    profile_picture = Column(LargeBinary, nullable=True)
    profile_file = Column(String)


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
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(String)
    completed=Column(Boolean,default=False)
    priority=Column(Integer,default=1)
    created_at = Column(String)
    updated_at = Column(String, default="Not updated yet")
    deleted = Column(Boolean, default=False)
