from app.config import supabase
from .schemas import SignupSchema, LoginSchema, UserRole
from fastapi import HTTPException, status, Request
from fastapi.security import (
    OAuth2PasswordBearer,
)
from fastapi import Depends
from jose import jwt
from app.config import SUPABASE_JWT_SECRET


async def create_user(user: SignupSchema):
    user_exists = supabase.table("user").select("*").eq("email", user.email).execute()
    if user_exists.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    response = supabase.auth.sign_up({"email": user.email, "password": user.password})

    if not response.user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user",
        )
    supabase.table("user").insert(
        {"email": user.email, "username": user.username, "role": UserRole.user.value}
    ).execute()

    return {"message": "User created successfully.", "user": response.user}


async def sign_in_user(user: LoginSchema):
    response = supabase.auth.sign_in_with_password(
        {"email": user.email, "password": user.password}
    )

    if not response.user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password",
        )

    return {
        "message": "Login successful",
        "user": response.user,
        "session": response.session,
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = supabase.auth.get_user(token)
    if user.user is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return user.user


async def sign_out_user():
    supabase.auth.sign_out()
