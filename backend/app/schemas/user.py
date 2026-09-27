from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: Optional[str] = "operator"


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    is_active: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str
