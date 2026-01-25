"""
Application configuration using Pydantic Settings
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    app_name: str = "Yellow"
    app_env: str = "development"
    secret_key: str = "change-me-in-production"
    frontend_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/yellow"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Pinecone
    pinecone_api_key: str = ""
    pinecone_index: str = "yellow-articles"
    
    # OpenAI
    openai_api_key: str = ""
    
    # Stytch
    stytch_project_id: str = ""
    stytch_secret: str = ""
    stytch_env: str = "test"
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    
    # Resend
    resend_api_key: str = ""
    resend_from_email: str = "Yellow <hello@yellow.app>"
    
    # BrightData
    brightdata_username: str = ""
    brightdata_password: str = ""
    brightdata_host: str = "brd.superproxy.io:22225"
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra env vars not defined in Settings


@lru_cache()
def get_settings() -> Settings:
    return Settings()
