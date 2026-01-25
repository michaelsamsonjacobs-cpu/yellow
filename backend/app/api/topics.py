"""
Topics API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.db.models import Topic, Article, Outlet, User
from app.schemas import (
    TopicListResponse, TopicResponse, TopicDetailResponse,
    ArticleListResponse, ArticleBrief
)
from app.api.deps import get_current_active_subscriber

router = APIRouter()


@router.get("", response_model=TopicListResponse)
async def list_topics(
    target_date: Optional[date] = Query(None, description="Date to get topics for (defaults to today)"),
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    Get today's Top 20 US and Top 20 International topics.
    """
    if target_date is None:
        target_date = date.today()
    
    # Start of day
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())
    
    # Get US topics
    us_result = await db.execute(
        select(Topic)
        .where(
            Topic.category == "us",
            Topic.date >= day_start,
            Topic.date <= day_end
        )
        .order_by(Topic.article_count.desc())
        .limit(20)
    )
    us_topics = us_result.scalars().all()
    
    # Get International topics
    intl_result = await db.execute(
        select(Topic)
        .where(
            Topic.category == "intl",
            Topic.date >= day_start,
            Topic.date <= day_end
        )
        .order_by(Topic.article_count.desc())
        .limit(20)
    )
    intl_topics = intl_result.scalars().all()
    
    return TopicListResponse(
        us_topics=[TopicResponse.model_validate(t) for t in us_topics],
        intl_topics=[TopicResponse.model_validate(t) for t in intl_topics],
        date=datetime.combine(target_date, datetime.min.time())
    )


@router.get("/{topic_id}", response_model=TopicDetailResponse)
async def get_topic(
    topic_id: UUID,
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """Get topic details by ID"""
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    return TopicDetailResponse.model_validate(topic)


@router.get("/{topic_id}/articles", response_model=ArticleListResponse)
async def get_topic_articles(
    topic_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("score", regex="^(score|outlet|date)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    Get articles covering a specific topic.
    Paginated and sortable.
    """
    # Verify topic exists
    topic_result = await db.execute(
        select(Topic).where(Topic.id == topic_id)
    )
    if not topic_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Build query
    query = (
        select(Article, Outlet)
        .join(Outlet)
        .where(Article.topic_id == topic_id)
    )
    
    # Sorting
    if sort_by == "score":
        order_col = Article.score
    elif sort_by == "outlet":
        order_col = Outlet.name
    else:  # date
        order_col = Article.published_at
    
    if sort_order == "desc":
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())
    
    # Count total
    count_query = select(func.count(Article.id)).where(Article.topic_id == topic_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    rows = result.all()
    
    articles = []
    for article, outlet in rows:
        articles.append(ArticleBrief(
            id=article.id,
            headline=article.headline,
            url=article.url,
            score=article.score,
            outlet_name=outlet.name,
            outlet_domain=outlet.domain,
            published_at=article.published_at,
            has_redraft=article.redraft_body is not None
        ))
    
    return ArticleListResponse(
        articles=articles,
        total=total,
        page=page,
        page_size=page_size
    )
