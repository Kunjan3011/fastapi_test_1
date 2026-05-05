from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(default="user")
    city: str


class TaskView(BaseModel):
    id:int
    name: str
    description: str
    created_at: str
    updated_at: str = Field(default="Not updated yet")


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    name: str
    description: str


