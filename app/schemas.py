from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)
    role: str = Field(default="user")


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
    completed: str
    created_at: str
    updated_at: str = Field(default="Not updated yet")


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    name: str = Field(default="Task")
    description: str = Field(default="None")
    priority: int = Field(gt=0, lt=6, default=1)
    completed: str = Field(default="no")
