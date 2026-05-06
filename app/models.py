from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary

from app.database import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    city = Column(String, index=True)
    ip = Column(String)
    role = Column(String, default="users")
    profile_picture = Column(LargeBinary, nullable=True)
    profile_file=Column(String)
    # location=Column(String)


class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(String)
    created_at = Column(String)
    updated_at=Column(String,default="Not updated yet")
    deleted=Column(String,default="False")
