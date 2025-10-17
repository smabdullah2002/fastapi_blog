from fastapi import APIRouter
from .auth import route_user
from .blog import route_blog

api_router = APIRouter()

# include the user authentication routes
api_router.include_router(route_user.router, prefix="", tags=["auth"])
# include the blog routes
api_router.include_router(route_blog.router, prefix="", tags=["blog"])
