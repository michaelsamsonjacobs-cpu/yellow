"""
Article Scoring Tasks
"""
import asyncio
from datetime import datetime
from celery import shared_task
from sqlalchemy import select, func

from app.tasks.celery_app import celery_app
from app.services.scoring import analyze_article, violations_to_json
from app.services.redraft import generate_redraft, redraft_to_json
from app.services.vectordb import store_article, query_historical_context, format_context_for_scoring
from app.db.database import AsyncSessionLocal
from app.db.models import Article, Outlet, ScoringAudit
from app.services.skew import SkewCalculator
from app.services.firestore_sync import sync_article_to_firestore, sync_outlet_to_firestore


async def _get_unscored_articles(limit: int = 100) -> list[Article]:
    """Get articles that haven't been scored yet"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Article)
            .where(Article.score.is_(None))
            .order_by(Article.scraped_at.asc())
            .limit(limit)
        )
        return result.scalars().all()


async def _score_single_article(article_id: str) -> bool:
    """Score a single article and update database"""
    async with AsyncSessionLocal() as db:
        # Get article with outlet
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            return False
        
        # Get outlet
        outlet_result = await db.execute(
            select(Outlet).where(Outlet.id == article.outlet_id)
        )
        outlet = outlet_result.scalar_one_or_none()
        
        # Get historical context from vector DB
        try:
            context = await query_historical_context(
                article.headline,
                outlet.domain if outlet else "",
                exclude_article_id=str(article.id)
            )
            context_str = format_context_for_scoring(context)
        except Exception as e:
            print(f"Context retrieval error: {e}")
            context_str = ""
        
        # Run scoring
        result = await analyze_article(
            headline=article.headline,
            body=article.body,
            outlet_name=outlet.name if outlet else "Unknown",
            historical_context=context_str
        )
        
        # Update article with score
        article.score = result.final_score
        article.violations = violations_to_json(result.violations)
        article.scored_at = datetime.utcnow()
        
        # Generate redraft if needed
        if result.needs_redraft:
            redraft = await generate_redraft(
                article.headline,
                article.body,
                result.violations
            )
            article.redraft_headline = redraft.redraft_headline
            article.redraft_body = redraft.redraft_body
            article.redraft_diff = redraft_to_json(redraft)
        
        # Create scoring audit
        audit = ScoringAudit(
            article_id=article.id,
            initial_score=100,
            final_score=result.final_score,
            verification_score=result.verification_score,
            neutrality_score=result.neutrality_score,
            fairness_score=result.fairness_score,
            violations_detail=violations_to_json(result.violations),
            model_used="gpt-4-turbo-preview",
            processing_time_ms=result.processing_time_ms
        )
        db.add(audit)
        
        # Store in vector DB for future context
        try:
            await store_article(
                article_id=str(article.id),
                headline=article.headline,
                body=article.body,
                outlet_domain=outlet.domain if outlet else "",
                topic_slug=str(article.topic_id) if article.topic_id else "",
                published_at=article.published_at or datetime.utcnow(),
                score=result.final_score
            )
        except Exception as e:
            print(f"Vector storage error: {e}")
        
        await db.commit()
        
        # Sync to Firestore
        try:
            sync_article_to_firestore(article, outlet.name if outlet else "Unknown")
        except Exception as e:
            print(f"Firestore article sync error: {e}")
            
        return True


async def _update_outlet_batting_average(outlet_id: str) -> None:
    """Recalculate batting average for an outlet"""
    async with AsyncSessionLocal() as db:
        # Calculate average score
        result = await db.execute(
            select(func.avg(Article.score), func.count(Article.id))
            .where(
                Article.outlet_id == outlet_id,
                Article.score.isnot(None)
            )
        )
        row = result.one()
        avg_score = row[0] or 0
        total_articles = row[1] or 0
        
        # Update outlet
        outlet_result = await db.execute(
            select(Outlet).where(Outlet.id == outlet_id)
        )
        outlet = outlet_result.scalar_one_or_none()
        
        if outlet:
            # Calculate "UN Factor" Skew Penalty
            calculator = SkewCalculator(db)
            skew_data = calculator.calculate_outlet_skew(outlet_id)
            skew_penalty = skew_data.get("skew_penalty", 0)
            
            # Apply penalty
            final_score = avg_score - skew_penalty
            
            # Ensure proper rounding and bounds (0-100)
            outlet.batting_average = max(0, min(100, round(final_score, 1)))
            outlet.total_articles = total_articles
            await db.commit()
            
            # Sync to Firestore
            try:
                sync_outlet_to_firestore(outlet)
            except Exception as e:
                print(f"Firestore outlet sync error: {e}")
            
            if skew_penalty > 0:
                print(f"  Applied skew penalty of -{skew_penalty} to {outlet.domain}")


@celery_app.task(name="app.tasks.scoring.score_pending_articles")
def score_pending_articles():
    """
    Daily task: Score all unscored articles.
    Runs at 9:00 AM UTC.
    """
    async def run():
        print(f"[{datetime.utcnow()}] Starting scoring pipeline...")
        
        articles = await _get_unscored_articles(limit=200)
        
        if not articles:
            print("No unscored articles found.")
            return 0
        
        print(f"Scoring {len(articles)} articles...")
        
        scored_count = 0
        for article in articles:
            try:
                success = await _score_single_article(str(article.id))
                if success:
                    scored_count += 1
                    print(f"  Scored article {article.id}: {article.headline[:50]}...")
            except Exception as e:
                print(f"  Error scoring article {article.id}: {e}")
            
            # Rate limiting for API calls
            await asyncio.sleep(1)
        
        print(f"[{datetime.utcnow()}] Scoring complete. Scored {scored_count} articles")
        return scored_count
    
    return asyncio.run(run())


@celery_app.task(name="app.tasks.scoring.score_single_article")
def score_single_article_task(article_id: str):
    """Score a single article by ID"""
    return asyncio.run(_score_single_article(article_id))


@celery_app.task(name="app.tasks.scoring.rollup_outlet_scores")
def rollup_outlet_scores():
    """
    Daily task: Recalculate batting averages for all outlets.
    Runs at 11:00 PM UTC.
    """
    async def run():
        print(f"[{datetime.utcnow()}] Rolling up outlet scores...")
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Outlet).where(Outlet.is_wire_service == False)
            )
            outlets = result.scalars().all()
        
        for outlet in outlets:
            await _update_outlet_batting_average(str(outlet.id))
            print(f"  Updated {outlet.domain}")
        
        print(f"[{datetime.utcnow()}] Rollup complete")
        return len(outlets)
    
    return asyncio.run(run())
