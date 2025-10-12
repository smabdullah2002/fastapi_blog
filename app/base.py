from fastapi import APIRouter
from .auth import route_user

api_router = APIRouter()

# include the user authentication routes
api_router.include_router(route_user.router, prefix="", tags=["auth"])
