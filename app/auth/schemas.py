from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    superuser = "superuser"
    user = "user"


class SignupSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
