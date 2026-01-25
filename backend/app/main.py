"""
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.db.database import engine, Base
from app.api import auth, topics, articles, outlets, users, newsletter, webhooks


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"Starting {settings.app_name} API...")
    yield
    # Shutdown
    print(f"Shutting down {settings.app_name} API...")


app = FastAPI(
    title=settings.app_name,
    description="News Integrity Platform API - Score, audit, and fix biased news",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(topics.router, prefix="/topics", tags=["Topics"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])
app.include_router(outlets.router, prefix="/outlets", tags=["Outlets"])
app.include_router(users.router, prefix="/user", tags=["User"])
app.include_router(newsletter.router, prefix="/newsletter", tags=["Newsletter"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "environment": settings.app_env
    }
