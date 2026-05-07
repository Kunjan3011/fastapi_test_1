from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(default="user")


class UserUpdate(BaseModel):
    city: str


class UserView(BaseModel):
    username: str
    role: str
    city: str
    country: str
    location: str


class TaskView(BaseModel):
    id: int
    name: str
    description: str
    priority: int
    completed: bool
    created_at: str
    updated_at: str = Field(default="Not updated yet")


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    name: str
    description: str
    priority: int
    completed: bool = Field(default=False)
