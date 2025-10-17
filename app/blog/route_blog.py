from .schemas import Category, BlogSchema
from app.config import supabase
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from .services import (
    create_blog_post,
    update_blog_post,
    delete_blog_post,
    list_blog_posts,
    get_blog_post,
    like_blog_post,
    comment_blog_post,
    CommentSchema,
    get_comments,
    bookmark_blog_post,
    unbookmark_blog_post,
    upload_image,
    get_blog_with_counts
)
from app.auth.route_user import get_current_user

router = APIRouter()


@router.post("/create_blog", status_code=status.HTTP_201_CREATED)
async def create_blog(blog: BlogSchema, user=Depends(get_current_user)):
    return await create_blog_post(blog, user)


@router.put("/update_blog/{blog_id}", status_code=status.HTTP_200_OK)
async def update_blog(blog_id: str, blog: BlogSchema, user=Depends(get_current_user)):
    return await update_blog_post(blog_id, blog, user)


@router.delete("/delete_blog/{blog_id}", status_code=status.HTTP_200_OK)
async def delete_blog(blog_id: str, user=Depends(get_current_user)):
    return await delete_blog_post(blog_id, user)


@router.get("/blogs", status_code=status.HTTP_200_OK)
async def list_blogs():
    return await list_blog_posts()


@router.get("/blog/{blog_id}", status_code=status.HTTP_200_OK)
async def get_blog(blog_id: str):
    return await get_blog_post(blog_id)


@router.post("/like_blog/{blog_id}", status_code=status.HTTP_200_OK)
async def like_blog(blog_id: str, user=Depends(get_current_user)):
    return await like_blog_post(blog_id, user)


@router.post("/comment", status_code=status.HTTP_200_OK)
async def comment(comment: CommentSchema, user=Depends(get_current_user)):
    return await comment_blog_post(comment, user)


@router.get("/blogs/{blog_id}/comments")
async def fetch_comments(blog_id: str, page: int = 1, per_page: int = 20):
    return await get_comments(blog_id, page, per_page)

@router.get("/blog/{blog_id}/with_counts", status_code=status.HTTP_200_OK)
async def get_blog_with_interaction_counts(blog_id: str):
    return await get_blog_with_counts(blog_id)


@router.post("/bookmark/{blog_id}", status_code=status.HTTP_200_OK)
async def bookmark(blog_id: str, user=Depends(get_current_user)):
    return await bookmark_blog_post(blog_id, user.id)


@router.delete("/unbookmark/{blog_id}", status_code=status.HTTP_200_OK)
async def unbookmark(blog_id: str, user=Depends(get_current_user)):
    return await unbookmark_blog_post(blog_id, user.id)


@router.post("/upload_image", status_code=status.HTTP_200_OK)
async def upload(file: UploadFile = File(...), user=Depends(get_current_user)):
    return await upload_image(file, user)
