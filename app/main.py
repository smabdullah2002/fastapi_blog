from fastapi import FastAPI
from .base import api_router

app= FastAPI(title="FastAPI Blog with Supabase", version="1.0.0")

app.include_router(api_router)
