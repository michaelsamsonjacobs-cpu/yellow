"""
Celery Configuration and App
"""
from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "yellow",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.discovery",
        "app.tasks.scraping",
        "app.tasks.scoring",
        "app.tasks.newsletter"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Scheduled tasks (cron jobs)
celery_app.conf.beat_schedule = {
    # Topic Discovery - 6:00 AM UTC daily
    "discover-topics-daily": {
        "task": "app.tasks.discovery.discover_and_store_topics",
        "schedule": crontab(hour=6, minute=0),
    },
    
    # Article Harvesting - 7:00 AM UTC daily
    "harvest-articles-daily": {
        "task": "app.tasks.scraping.harvest_all_outlets",
        "schedule": crontab(hour=7, minute=0),
    },
    
    # Scoring Pipeline - 9:00 AM UTC daily
    "score-articles-daily": {
        "task": "app.tasks.scoring.score_pending_articles",
        "schedule": crontab(hour=9, minute=0),
    },
    
    # Daily Briefing Newsletter - 2:00 PM UTC daily
    "send-daily-briefing": {
        "task": "app.tasks.newsletter.send_daily_briefing_to_all",
        "schedule": crontab(hour=14, minute=0),
    },
    
    # Outlet Score Rollup - 11:00 PM UTC daily
    "rollup-outlet-scores": {
        "task": "app.tasks.scoring.rollup_outlet_scores",
        "schedule": crontab(hour=23, minute=0),
    },
}
