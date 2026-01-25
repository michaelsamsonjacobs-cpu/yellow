"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import secrets
import uuid

from app.db.database import get_db
from app.db.models import User, Session, MagicLink
from app.schemas import (
    MagicLinkRequest, MagicLinkResponse,
    VerifyTokenResponse, AuthMeResponse, UserResponse
)
from app.api.deps import get_current_user
from app.services.email import send_magic_link_email
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a passwordless magic link.
    Sends an email with a login link.
    """
    email = request.email.lower().strip()
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Create magic link record
    magic_link = MagicLink(
        email=email,
        token=token,
        expires_at=expires_at
    )
    db.add(magic_link)
    await db.commit()
    
    # Build magic link URL
    link_url = f"{settings.frontend_url}/auth/verify?token={token}"
    
    # Send email
    try:
        await send_magic_link_email(email, link_url)
    except Exception as e:
        # Log but don't expose email errors to client
        print(f"Email send error: {e}")
    
    return MagicLinkResponse(email=email)


@router.get("/verify", response_model=VerifyTokenResponse)
async def verify_magic_link(
    token: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a magic link token and create a session.
    """
    # Find the magic link
    result = await db.execute(
        select(MagicLink).where(
            MagicLink.token == token,
            MagicLink.used == False,
            MagicLink.expires_at > datetime.utcnow()
        )
    )
    magic_link = result.scalar_one_or_none()
    
    if not magic_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired magic link"
        )
    
    # Mark as used
    magic_link.used = True
    
    # Find or create user
    result = await db.execute(
        select(User).where(User.email == magic_link.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(email=magic_link.email)
        db.add(user)
        await db.flush()
    
    # Create session
    session_token = secrets.token_urlsafe(64)
    session_expires = datetime.utcnow() + timedelta(days=30)
    
    session = Session(
        user_id=user.id,
        token=session_token,
        expires_at=session_expires
    )
    db.add(session)
    await db.commit()
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
        path="/"
    )
    
    return VerifyTokenResponse(
        access_token=session_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user by invalidating their session.
    """
    # Delete all user sessions
    await db.execute(
        Session.__table__.delete().where(Session.user_id == user.id)
    )
    await db.commit()
    
    # Clear cookie
    response.delete_cookie(key="session", path="/")
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AuthMeResponse)
async def get_me(user: User = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    return AuthMeResponse(user=UserResponse.model_validate(user))
