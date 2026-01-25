"""
User API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from app.db.database import get_db
from app.db.models import User
from app.schemas import (
    UserResponse, UserUpdate, SubscribeResponse, PortalResponse
)
from app.api.deps import get_current_user
from app.config import get_settings

router = APIRouter()
settings = get_settings()

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


@router.get("", response_model=UserResponse)
async def get_user(user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.model_validate(user)


@router.patch("", response_model=UserResponse)
async def update_user(
    update: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    if update.newsletter_opt_in is not None:
        user.newsletter_opt_in = update.newsletter_opt_in
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.post("/subscribe", response_model=SubscribeResponse)
async def create_checkout_session(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription.
    Returns the checkout URL.
    """
    # Create or get Stripe customer
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            metadata={"user_id": str(user.id)}
        )
        user.stripe_customer_id = customer.id
        await db.commit()
    
    # Create checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": settings.stripe_price_id,
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{settings.frontend_url}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.frontend_url}/pricing?cancelled=true",
            metadata={"user_id": str(user.id)}
        )
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return SubscribeResponse(checkout_url=checkout_session.url)


@router.post("/portal", response_model=PortalResponse)
async def create_portal_session(
    user: User = Depends(get_current_user)
):
    """
    Create Stripe billing portal session.
    Allows user to manage subscription.
    """
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found"
        )
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{settings.frontend_url}/settings"
        )
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return PortalResponse(portal_url=portal_session.url)


@router.patch("/newsletter", response_model=UserResponse)
async def toggle_newsletter(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle newsletter preference"""
    user.newsletter_opt_in = not user.newsletter_opt_in
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)
