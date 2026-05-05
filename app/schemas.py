from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = Field(default="user")
    city: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    name:str
    description:str