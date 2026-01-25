"""
Article Scraping Tasks
"""
import asyncio
from datetime import datetime, date
from celery import shared_task
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.scraper.harvester import scrape_topic_from_outlet, ScrapedArticle
from app.scraper.outlets import get_scored_outlets, OutletConfig
from app.db.database import AsyncSessionLocal
from app.db.models import Topic, Article, Outlet


async def _get_todays_topics() -> list[Topic]:
    """Get today's topics from database"""
    async with AsyncSessionLocal() as db:
        today = date.today()
        day_start = datetime.combine(today, datetime.min.time())
        day_end = datetime.combine(today, datetime.max.time())
        
        result = await db.execute(
            select(Topic).where(
                Topic.date >= day_start,
                Topic.date <= day_end
            )
        )
        return result.scalars().all()


async def _get_or_create_outlet(config: OutletConfig) -> Outlet:
    """Get or create outlet in database"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Outlet).where(Outlet.domain == config.domain)
        )
        outlet = result.scalar_one_or_none()
        
        if not outlet:
            outlet = Outlet(
                name=config.name,
                domain=config.domain,
                monthly_visits=config.monthly_visits,
                is_wire_service=config.is_wire_service
            )
            db.add(outlet)
            await db.commit()
            await db.refresh(outlet)
        
        return outlet


async def _store_article(
    scraped: ScrapedArticle,
    outlet_id: str,
    topic_id: str
) -> bool:
    """Store scraped article in database"""
    async with AsyncSessionLocal() as db:
        # Check if already exists
        result = await db.execute(
            select(Article).where(Article.url == scraped.url)
        )
        if result.scalar_one_or_none():
            return False  # Already exists
        
        article = Article(
            outlet_id=outlet_id,
            topic_id=topic_id,
            headline=scraped.headline,
            body=scraped.body,
            url=scraped.url,
            author=scraped.author,
            published_at=scraped.published_at
        )
        db.add(article)
        await db.commit()
        return True


async def _update_topic_count(topic_id: str) -> None:
    """Update article count for a topic"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        topic = result.scalar_one_or_none()
        if topic:
            topic.article_count += 1
            await db.commit()


async def _harvest_outlet_for_topics(
    outlet_config: OutletConfig,
    topics: list[Topic]
) -> int:
    """Harvest articles from one outlet for all topics"""
    outlet = await _get_or_create_outlet(outlet_config)
    articles_stored = 0
    
    for topic in topics:
        # Use topic name as search query
        articles = await scrape_topic_from_outlet(
            outlet_config,
            topic.name,
            max_articles=3  # Limit per topic per outlet
        )
        
        for article in articles:
            stored = await _store_article(
                article,
                str(outlet.id),
                str(topic.id)
            )
            if stored:
                articles_stored += 1
                await _update_topic_count(str(topic.id))
        
        # Rate limiting between topics
        await asyncio.sleep(2)
    
    return articles_stored


@celery_app.task(name="app.tasks.scraping.harvest_all_outlets")
def harvest_all_outlets():
    """
    Daily task: Scrape all outlets for today's topics.
    Runs at 7:00 AM UTC.
    """
    async def run():
        print(f"[{datetime.utcnow()}] Starting article harvesting...")
        
        topics = await _get_todays_topics()
        if not topics:
            print("No topics found for today. Skipping harvest.")
            return 0
        
        print(f"Harvesting for {len(topics)} topics")
        
        outlets = get_scored_outlets()
        total_articles = 0
        
        for outlet_config in outlets:
            print(f"Harvesting {outlet_config.domain}...")
            try:
                count = await _harvest_outlet_for_topics(outlet_config, topics)
                total_articles += count
                print(f"  Stored {count} articles from {outlet_config.domain}")
            except Exception as e:
                print(f"  Error harvesting {outlet_config.domain}: {e}")
            
            # Rate limiting between outlets
            await asyncio.sleep(5)
        
        print(f"[{datetime.utcnow()}] Harvesting complete. Total: {total_articles} articles")
        return total_articles
    
    return asyncio.run(run())


@celery_app.task(name="app.tasks.scraping.harvest_single_outlet")
def harvest_single_outlet(domain: str):
    """Harvest articles from a single outlet"""
    from app.scraper.outlets import get_outlet_config
    
    async def run():
        config = get_outlet_config(domain)
        if not config:
            print(f"No config found for {domain}")
            return 0
        
        topics = await _get_todays_topics()
        if not topics:
            return 0
        
        return await _harvest_outlet_for_topics(config, topics)
    
    return asyncio.run(run())


if __name__ == "__main__":
    _ = harvest_all_outlets()
