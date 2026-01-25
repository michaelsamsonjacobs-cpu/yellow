"""
Outlets API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import List
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import Outlet, Article, User
from app.schemas import (
    OutletResponse, OutletBrief, OutletListResponse,
    OutletHistoryResponse, OutletHistoryPoint, TopViolation
)
from app.api.deps import get_current_active_subscriber
from app.services.skew import SkewCalculator

router = APIRouter()


def calculate_top_violations(articles: List[Article]) -> List[TopViolation]:
    """Calculate top violation types for an outlet"""
    violation_counts = {}
    total_violations = 0
    
    for article in articles:
        if article.violations:
            for v in article.violations.get("violations", []):
                v_type = v.get("type", "Unknown")
                violation_counts[v_type] = violation_counts.get(v_type, 0) + 1
                total_violations += 1
    
    if total_violations == 0:
        return []
    
    # Sort by count and get top 5
    sorted_violations = sorted(
        violation_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return [
        TopViolation(
            type=v_type,
            percentage=round((count / total_violations) * 100, 1),
            count=count
        )
        for v_type, count in sorted_violations
    ]


@router.get("", response_model=OutletListResponse)
async def list_outlets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("batting_average", regex="^(batting_average|name|total_articles)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    List all monitored outlets with their scores.
    """
    # Build query
    query = select(Outlet).where(Outlet.is_wire_service == False)
    
    # Sorting
    if sort_by == "batting_average":
        order_col = Outlet.batting_average
    elif sort_by == "name":
        order_col = Outlet.name
    else:  # total_articles
        order_col = Outlet.total_articles
    
    if sort_order == "desc":
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())
    
    # Count total
    count_result = await db.execute(
        select(func.count(Outlet.id)).where(Outlet.is_wire_service == False)
    )
    total = count_result.scalar()
    
    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    outlets = result.scalars().all()
    
    return OutletListResponse(
        outlets=[OutletBrief.model_validate(o) for o in outlets],
        total=total
    )


@router.get("/rankings")
async def get_outlet_rankings(
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    Get today's highest and lowest scoring outlets.
    Used for the live ticker on marketing site.
    """
    # Highest scoring (non-wire)
    highest_result = await db.execute(
        select(Outlet)
        .where(Outlet.is_wire_service == False, Outlet.total_articles > 0)
        .order_by(Outlet.batting_average.desc())
        .limit(1)
    )
    highest = highest_result.scalar_one_or_none()
    
    # Lowest scoring
    lowest_result = await db.execute(
        select(Outlet)
        .where(Outlet.is_wire_service == False, Outlet.total_articles > 0)
        .order_by(Outlet.batting_average.asc())
        .limit(1)
    )
    lowest = lowest_result.scalar_one_or_none()
    
    return {
        "highest": OutletBrief.model_validate(highest) if highest else None,
        "lowest": OutletBrief.model_validate(lowest) if lowest else None,
        "as_of": datetime.utcnow()
    }


@router.get("/{outlet_id}", response_model=OutletResponse)
async def get_outlet(
    outlet_id: UUID,
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    Get outlet details ("Baseball Card").
    Includes batting average, bias tilt, and top violations.
    """
    result = await db.execute(
        select(Outlet).where(Outlet.id == outlet_id)
    )
    outlet = result.scalar_one_or_none()
    
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outlet not found"
        )
    
    # Get recent articles for violation analysis
    articles_result = await db.execute(
        select(Article)
        .where(Article.outlet_id == outlet_id)
        .order_by(Article.scraped_at.desc())
        .limit(100)
    )
    recent_articles = articles_result.scalars().all()
    
    top_violations = calculate_top_violations(recent_articles)
    
    return OutletResponse(
        id=outlet.id,
        name=outlet.name,
        domain=outlet.domain,
        logo_url=outlet.logo_url,
        batting_average=outlet.batting_average,
        bias_tilt=outlet.bias_tilt,
        total_articles=outlet.total_articles,
        monthly_visits=outlet.monthly_visits,
        is_wire_service=outlet.is_wire_service,
        top_violations=top_violations
    )


@router.get("/{outlet_id}/skew")
async def get_outlet_skew(
    outlet_id: UUID,
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    Get outlet topic skew analysis ("UN Factor").
    """
    calculator = SkewCalculator(db)
    skew_data = calculator.calculate_outlet_skew(outlet_id)
    return skew_data


@router.get("/{outlet_id}/history", response_model=OutletHistoryResponse)
async def get_outlet_history(
    outlet_id: UUID,
    days: int = Query(30, ge=7, le=180),
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    Get outlet score history over time.
    """
    # Get outlet
    result = await db.execute(
        select(Outlet).where(Outlet.id == outlet_id)
    )
    outlet = result.scalar_one_or_none()
    
    if not outlet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outlet not found"
        )
    
    # Get daily aggregates
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Group by day and calculate averages
    articles_result = await db.execute(
        select(
            func.date(Article.scraped_at).label("date"),
            func.avg(Article.score).label("avg_score"),
            func.count(Article.id).label("article_count")
        )
        .where(
            Article.outlet_id == outlet_id,
            Article.scraped_at >= start_date,
            Article.score.isnot(None)
        )
        .group_by(func.date(Article.scraped_at))
        .order_by(func.date(Article.scraped_at))
    )
    
    history = []
    for row in articles_result:
        history.append(OutletHistoryPoint(
            date=datetime.combine(row.date, datetime.min.time()),
            score=round(row.avg_score, 1),
            article_count=row.article_count
        ))
    
    return OutletHistoryResponse(
        outlet=OutletBrief.model_validate(outlet),
        history=history
    )
