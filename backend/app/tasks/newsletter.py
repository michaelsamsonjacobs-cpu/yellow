"""
Newsletter Tasks
"""
import asyncio
from datetime import datetime, date
from typing import List, Dict
from celery import shared_task
from sqlalchemy import select, func

from app.tasks.celery_app import celery_app
from app.services.email import send_daily_briefing
from app.db.database import AsyncSessionLocal
from app.db.models import NewsletterSubscriber, User, Article, Outlet


async def _get_all_newsletter_recipients() -> List[Dict]:
    """Get all active newsletter subscribers"""
    async with AsyncSessionLocal() as db:
        # Get newsletter subscribers
        result = await db.execute(
            select(NewsletterSubscriber).where(NewsletterSubscriber.is_active == True)
        )
        subscribers = result.scalars().all()
        
        recipients = [
            {"email": s.email, "unsubscribe_token": s.unsubscribe_token}
            for s in subscribers
        ]
        
        # Also get app users who opted in
        user_result = await db.execute(
            select(User).where(User.newsletter_opt_in == True)
        )
        users = user_result.scalars().all()
        
        # Get or generate unsubscribe tokens for users
        existing_emails = {r["email"] for r in recipients}
        for user in users:
            if user.email not in existing_emails:
                # User doesn't have newsletter subscription - create one
                import secrets
                token = secrets.token_urlsafe(32)
                recipients.append({
                    "email": user.email,
                    "unsubscribe_token": token
                })
        
        return recipients


async def _get_daily_briefing_data() -> Dict:
    """Get data for daily briefing email"""
    async with AsyncSessionLocal() as db:
        today = date.today()
        day_start = datetime.combine(today, datetime.min.time())
        
        # Top 3 most accurate (highest scoring)
        top_accurate_result = await db.execute(
            select(Article, Outlet)
            .join(Outlet)
            .where(
                Article.scored_at >= day_start,
                Article.score.isnot(None),
                Outlet.is_wire_service == False
            )
            .order_by(Article.score.desc())
            .limit(3)
        )
        top_accurate = [
            {
                "id": str(article.id),
                "headline": article.headline,
                "score": article.score,
                "outlet": outlet.name
            }
            for article, outlet in top_accurate_result
        ]
        
        # Top 3 most biased (lowest scoring, with redraft)
        top_biased_result = await db.execute(
            select(Article, Outlet)
            .join(Outlet)
            .where(
                Article.scored_at >= day_start,
                Article.score.isnot(None),
                Article.redraft_body.isnot(None),
                Outlet.is_wire_service == False
            )
            .order_by(Article.score.asc())
            .limit(3)
        )
        top_biased = [
            {
                "id": str(article.id),
                "headline": article.headline,
                "score": article.score,
                "outlet": outlet.name
            }
            for article, outlet in top_biased_result
        ]
        
        # Highest scoring outlet today
        highest_result = await db.execute(
            select(Outlet)
            .where(Outlet.is_wire_service == False, Outlet.total_articles > 0)
            .order_by(Outlet.batting_average.desc())
            .limit(1)
        )
        highest = highest_result.scalar_one_or_none()
        
        # Lowest scoring outlet today
        lowest_result = await db.execute(
            select(Outlet)
            .where(Outlet.is_wire_service == False, Outlet.total_articles > 0)
            .order_by(Outlet.batting_average.asc())
            .limit(1)
        )
        lowest = lowest_result.scalar_one_or_none()
        
        return {
            "top_accurate": top_accurate,
            "top_biased": top_biased,
            "highest_outlet": {
                "name": highest.name if highest else "N/A",
                "score": highest.batting_average if highest else 0
            },
            "lowest_outlet": {
                "name": lowest.name if lowest else "N/A",
                "score": lowest.batting_average if lowest else 0
            }
        }


@celery_app.task(name="app.tasks.newsletter.send_daily_briefing_to_all")
def send_daily_briefing_to_all():
    """
    Daily task: Send briefing newsletter to all subscribers.
    Runs at 2:00 PM UTC.
    """
    async def run():
        print(f"[{datetime.utcnow()}] Preparing daily briefing...")
        
        # Get briefing data
        data = await _get_daily_briefing_data()
        
        if not data["top_accurate"] and not data["top_biased"]:
            print("No articles to report. Skipping newsletter.")
            return 0
        
        # Get recipients
        recipients = await _get_all_newsletter_recipients()
        
        print(f"Sending to {len(recipients)} subscribers...")
        
        sent_count = 0
        for recipient in recipients:
            try:
                await send_daily_briefing(
                    email=recipient["email"],
                    unsubscribe_token=recipient["unsubscribe_token"],
                    top_accurate=data["top_accurate"],
                    top_biased=data["top_biased"],
                    highest_outlet=data["highest_outlet"],
                    lowest_outlet=data["lowest_outlet"]
                )
                sent_count += 1
            except Exception as e:
                print(f"  Error sending to {recipient['email']}: {e}")
            
            # Rate limit
            await asyncio.sleep(0.1)
        
        print(f"[{datetime.utcnow()}] Sent {sent_count} briefings")
        return sent_count
    
    return asyncio.run(run())
