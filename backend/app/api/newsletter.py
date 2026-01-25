"""
Newsletter API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import secrets

from app.db.database import get_db
from app.db.models import NewsletterSubscriber
from app.schemas import (
    NewsletterSubscribeRequest, NewsletterSubscribeResponse,
    NewsletterUnsubscribeRequest, NewsletterUnsubscribeResponse
)
from app.services.email import send_newsletter_welcome_email

router = APIRouter()


@router.post("/subscribe", response_model=NewsletterSubscribeResponse)
async def subscribe_to_newsletter(
    request: NewsletterSubscribeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Subscribe to the daily briefing newsletter.
    No authentication required.
    """
    email = request.email.lower().strip()
    
    # Check if already subscribed
    result = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        if existing.is_active:
            # Already subscribed
            return NewsletterSubscribeResponse(
                message="You're already subscribed!",
                email=email
            )
        else:
            # Reactivate
            existing.is_active = True
            existing.unsubscribed_at = None
            await db.commit()
            return NewsletterSubscribeResponse(
                message="Welcome back! You've been resubscribed.",
                email=email
            )
    
    # Create new subscriber
    unsubscribe_token = secrets.token_urlsafe(32)
    subscriber = NewsletterSubscriber(
        email=email,
        unsubscribe_token=unsubscribe_token,
        source="website"
    )
    db.add(subscriber)
    await db.commit()
    
    # Send welcome email
    try:
        await send_newsletter_welcome_email(email, unsubscribe_token)
    except Exception as e:
        print(f"Welcome email error: {e}")
    
    return NewsletterSubscribeResponse(
        message="Successfully subscribed to the newsletter",
        email=email
    )


@router.post("/unsubscribe", response_model=NewsletterUnsubscribeResponse)
async def unsubscribe_from_newsletter(
    request: NewsletterUnsubscribeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Unsubscribe from the newsletter using token.
    """
    result = await db.execute(
        select(NewsletterSubscriber).where(
            NewsletterSubscriber.unsubscribe_token == request.token
        )
    )
    subscriber = result.scalar_one_or_none()
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid unsubscribe token"
        )
    
    if not subscriber.is_active:
        return NewsletterUnsubscribeResponse(
            message="You're already unsubscribed"
        )
    
    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.utcnow()
    await db.commit()
    
    return NewsletterUnsubscribeResponse(
        message="Successfully unsubscribed from the newsletter"
    )


@router.get("/unsubscribe")
async def unsubscribe_via_link(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Unsubscribe via GET request (for email link clicks).
    """
    result = await db.execute(
        select(NewsletterSubscriber).where(
            NewsletterSubscriber.unsubscribe_token == token
        )
    )
    subscriber = result.scalar_one_or_none()
    
    if not subscriber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid unsubscribe token"
        )
    
    if subscriber.is_active:
        subscriber.is_active = False
        subscriber.unsubscribed_at = datetime.utcnow()
        await db.commit()
    
    return {"message": "You have been unsubscribed from the Yellow newsletter."}
