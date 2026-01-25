"""
Topic Discovery Tasks
"""
import asyncio
from datetime import datetime
from celery import shared_task

from app.tasks.celery_app import celery_app
from app.scraper.discovery import discover_daily_topics, DiscoveredTopic
from app.db.database import AsyncSessionLocal
from app.db.models import Topic
from app.services.firestore_sync import sync_topic_to_firestore


async def _store_topics(topics: list[DiscoveredTopic]) -> int:
    """Store discovered topics in database"""
    async with AsyncSessionLocal() as db:
        count = 0
        for topic_data in topics:
            topic = Topic(
                name=topic_data.name,
                slug=topic_data.slug,
                category=topic_data.category,
                keywords={"keywords": topic_data.keywords},
                date=datetime.utcnow(),
                article_count=0
            )
            db.add(topic)
            count += 1
            
            # Sync to Firestore
            try:
                sync_topic_to_firestore(topic)
            except Exception as e:
                print(f"Firestore topic sync error: {e}")
        
        await db.commit()
        return count


@celery_app.task(name="app.tasks.discovery.discover_and_store_topics")
def discover_and_store_topics():
    """
    Daily task: Discover topics from wire services and store in DB.
    Runs at 6:00 AM UTC.
    """
    async def run():
        print(f"[{datetime.utcnow()}] Starting topic discovery...")
        
        us_topics, intl_topics = await discover_daily_topics()
        
        print(f"Discovered {len(us_topics)} US topics, {len(intl_topics)} Intl topics")
        
        all_topics = us_topics + intl_topics
        count = await _store_topics(all_topics)
        
        print(f"[{datetime.utcnow()}] Stored {count} topics")
        return count
    
    return asyncio.run(run())


if __name__ == "__main__":
    _ = discover_and_store_topics()
