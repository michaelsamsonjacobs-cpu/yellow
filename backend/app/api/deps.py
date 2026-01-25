"""
Authentication dependencies
"""
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
import uuid

from app.db.database import get_db
from app.db.models import User, Session


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None, alias="session"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from either:
    - Bearer token in Authorization header
    - Session cookie
    """
    token = None
    
    # Try Bearer token first
    if credentials:
        token = credentials.credentials
    # Fall back to session cookie
    elif session_token:
        token = session_token
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Find session
    result = await db.execute(
        select(Session).where(
            Session.token == token,
            Session.expires_at > datetime.utcnow()
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == session.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


async def get_current_active_subscriber(
    user: User = Depends(get_current_user)
) -> User:
    """Require user has active subscription"""
    if user.subscription_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required",
        )
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None, alias="session"),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    try:
        return await get_current_user(credentials, session_token, db)
    except HTTPException:
        return None
