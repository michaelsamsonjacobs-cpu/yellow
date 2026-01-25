"""
Webhook handlers (Stripe)
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe

from app.db.database import get_db
from app.db.models import User
from app.schemas import StripeWebhookResponse
from app.config import get_settings

router = APIRouter()
settings = get_settings()

stripe.api_key = settings.stripe_secret_key


@router.post("/stripe", response_model=StripeWebhookResponse)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    Updates user subscription status.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle the event
    event_type = event["type"]
    data = event["data"]["object"]
    
    if event_type == "checkout.session.completed":
        await handle_checkout_completed(data, db)
    
    elif event_type == "customer.subscription.created":
        await handle_subscription_created(data, db)
    
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data, db)
    
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(data, db)
    
    elif event_type == "invoice.payment_failed":
        await handle_payment_failed(data, db)
    
    return StripeWebhookResponse(received=True)


async def handle_checkout_completed(data: dict, db: AsyncSession):
    """Handle successful checkout"""
    customer_id = data.get("customer")
    subscription_id = data.get("subscription")
    
    if not customer_id:
        return
    
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.subscription_status = "active"
        user.subscription_id = subscription_id
        await db.commit()


async def handle_subscription_created(data: dict, db: AsyncSession):
    """Handle new subscription"""
    customer_id = data.get("customer")
    subscription_id = data.get("id")
    status_val = data.get("status")
    
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.subscription_id = subscription_id
        user.subscription_status = status_val if status_val == "active" else "inactive"
        await db.commit()


async def handle_subscription_updated(data: dict, db: AsyncSession):
    """Handle subscription updates"""
    customer_id = data.get("customer")
    status_val = data.get("status")
    
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Map Stripe status to our status
        status_map = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "cancelled",
            "unpaid": "inactive",
            "incomplete": "inactive",
            "incomplete_expired": "inactive",
            "trialing": "active"
        }
        user.subscription_status = status_map.get(status_val, "inactive")
        await db.commit()


async def handle_subscription_deleted(data: dict, db: AsyncSession):
    """Handle subscription cancellation"""
    customer_id = data.get("customer")
    
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.subscription_status = "cancelled"
        user.subscription_id = None
        await db.commit()


async def handle_payment_failed(data: dict, db: AsyncSession):
    """Handle failed payment"""
    customer_id = data.get("customer")
    
    result = await db.execute(
        select(User).where(User.stripe_customer_id == customer_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.subscription_status = "past_due"
        await db.commit()
        
        # TODO: Send payment failed email via Resend
