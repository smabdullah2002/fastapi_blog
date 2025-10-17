from app.config import supabase
from fastapi import HTTPException, status, Depends, UploadFile, File
from .schemas import Category, BlogSchema, CommentSchema
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def create_blog_post(blog: BlogSchema, user: Depends(oauth2_scheme)):
    current_user = supabase.table("user").select("*").eq("id", user.id).execute()
    user_data = current_user.data
    # print("========",user_data[0]['role'])

    if user_data[0]["role"] != "superuser":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create a blog post.",
        )

    response = (
        supabase.table("blog")
        .insert(
            {
                "title": blog.title,
                "content": blog.content,
                "category": blog.category,
                "img_url": str(blog.img_url),
                "author_id": user.id,
            }
        )
        .execute()
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create blog post.",
        )
    return response.data


async def update_blog_post(
    blog_id: str, blog: BlogSchema, user: Depends(oauth2_scheme)
):
    current_user = supabase.table("user").select("*").eq("id", user.id).execute()
    user_data = current_user.data
    if user_data[0]["role"] != "superuser":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update a blog post.",
        )

    response = (
        supabase.table("blog")
        .update(
            {
                "title": blog.title,
                "content": blog.content,
                "category": blog.category,
                "img_url": str(blog.img_url),
            }
        )
        .eq("id", blog_id)
        .execute()
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update blog post.",
        )
    return response.data


async def delete_blog_post(blog_id: str, user: Depends(oauth2_scheme)):
    current_user = supabase.table("user").select("*").eq("id", user.id).execute()
    user_data = current_user.data
    if user_data[0]["role"] != "superuser":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete a blog post.",
        )

    response = supabase.table("blog").delete().eq("id", blog_id).execute()

    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete blog post.",
        )
    return {"detail": "Blog post deleted successfully"}


async def list_blog_posts():
    response = supabase.table("blog").select("*").execute()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch blog posts.",
        )
    return response.data


async def get_blog_post(blog_id: str):
    response = supabase.table("blog").select("*").eq("id", blog_id).execute()
    if not response or not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found.",
        )
    return response.data[0]


# async def like_blog_post(blog_id: str, user: Depends(oauth2_scheme)):
#     response = supabase.table("blog").select("*").eq("id", blog_id).execute()
#     if not response or not response.data:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Blog post not found.",
#         )
#     already_liked = (
#         supabase.table("likes")
#         .select("*")
#         .eq("blog_id", blog_id)
#         .eq("user_id", user.id)
#         .execute()
#     )
#     if already_liked:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="You have already liked this blog post.",
#         )
#         return
#     blog = response.data[0]
#     # likes = blog.get("likes", 0) + 1
#     # update_response = (
#     #     supabase.table("blog").update({"likes": likes}).eq("id", blog_id).execute()
#     # )
#     # if not update_response:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#     #         detail="Failed to like blog post.",
#     #     )
#     response = (
#         supabase.table("likes")
#         .insert({"blog_id": blog_id, "user_id": user.id})
#         .execute()
#     )
#     return {"detail": "Blog post liked successfully", "total_likes": likes}


async def like_blog_post(blog_id: str, user=Depends(oauth2_scheme)):
    # Check if the blog exists
    response = supabase.table("blog").select("id").eq("id", blog_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found."
        )

    # Check if user already liked this blog
    existing_like = (
        supabase.table("likes")
        .select("id")
        .eq("blog_id", blog_id)
        .eq("user_id", user.id)
        .execute()
    )

    if existing_like.data:
        # Unlike (remove like)
        supabase.table("likes").delete().eq("blog_id", blog_id).eq(
            "user_id", user.id
        ).execute()
        action = "unliked"
    else:
        # Like (insert new like)
        supabase.table("likes").insert(
            {"blog_id": blog_id, "user_id": user.id}
        ).execute()
        action = "liked"

    # Count total likes dynamically
    total_likes = (
        supabase.table("likes")
        .select("id", count="exact")
        .eq("blog_id", blog_id)
        .execute()
        .count
    )

    return {"detail": f"Blog post {action} successfully", "total_likes": total_likes}


async def get_blog_with_counts(blog_id: str):
    # get blog data
    blog_res = supabase.table("blog").select("*").eq("id", blog_id).limit(1).execute()
    if not blog_res.data:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog = blog_res.data[0]

    # count likes
    likes_res = (
        supabase.table("likes")
        .select("id", count="exact")
        .eq("blog_id", blog_id)
        .execute()
    )
    total_likes = likes_res.count or 0

    # count comments
    comments_res = (
        supabase.table("comments")
        .select("id", count="exact")
        .eq("blog_id", blog_id)
        .execute()
    )
    total_comments = comments_res.count or 0

    blog["total_likes"] = total_likes
    blog["total_comments"] = total_comments
    return blog


async def comment_blog_post(comment: CommentSchema, user: Depends(oauth2_scheme)):
    response = supabase.table("blog").select("*").eq("id", comment.blog_id).execute()
    if not response or not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found.",
        )
    response = (
        supabase.table("comments")
        .insert(
            {"blog_id": comment.blog_id, "user_id": user.id, "content": comment.content}
        )
        .execute()
    )
    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment.",
        )
    return {"detail": "Comment added successfully"}


async def get_comments(blog_id: str, page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    response = (
        supabase.table("comments")
        .select("*")
        .eq("blog_id", blog_id)
        .order("created_at", desc=False)
        .range(offset, offset + per_page - 1)
        .execute()
    )
    return response.data or []


async def bookmark_blog_post(blog_id: str, user_id: str):
    response = (
        supabase.table("bookmarks")
        .insert({"blog_id": blog_id, "user_id": user_id})
        .execute()
    )
    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bookmark blog post.",
        )
    return {"detail": "Blog post bookmarked successfully"}


async def unbookmark_blog_post(blog_id: str, user_id: str):
    response = (
        supabase.table("bookmarks")
        .delete()
        .eq("blog_id", blog_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove bookmark.",
        )
    return {"detail": "Bookmark removed successfully"}


async def upload_image(file: UploadFile = File(...), token=Depends(oauth2_scheme)):
    file_content = await file.read()
    file_path = f"uploads/{file.filename}"

    try:
        # Upload file to Supabase Storage
        supabase.storage.from_("blog-images").upload(
            file_path, file_content, {"content-type": file.content_type}
        )

        # Get public URL
        public_url_response = supabase.storage.from_("blog-images").get_public_url(
            file_path
        )
        return {"img_url": public_url_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
