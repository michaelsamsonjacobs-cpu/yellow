"""
Articles API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List

from app.db.database import get_db
from app.db.models import Article, Outlet, Topic, User
from app.schemas import (
    ArticleResponse, ArticleRedraft, DiffSegment,
    ViolationDetail, OutletBrief, TopicResponse
)
from app.api.deps import get_current_active_subscriber

router = APIRouter()


def parse_violations(violations_json: dict) -> List[ViolationDetail]:
    """Parse violations JSON into structured list"""
    if not violations_json:
        return []
    
    violations = []
    for v in violations_json.get("violations", []):
        violations.append(ViolationDetail(
            type=v.get("type", "Unknown"),
            description=v.get("description", ""),
            deduction=v.get("deduction", 0),
            instances=v.get("instances", [])
        ))
    return violations


def create_diff_segments(original: str, redraft: str, diff_data: dict = None) -> List[DiffSegment]:
    """
    Create diff segments showing changes.
    For now, using simple word-level diff. Can be enhanced with actual diff algorithm.
    """
    if diff_data and "segments" in diff_data:
        return [DiffSegment(**s) for s in diff_data["segments"]]
    
    # Simple fallback - mark whole original as removed, whole redraft as added
    # In production, use difflib or similar for word-level diff
    segments = []
    if original != redraft:
        segments.append(DiffSegment(type="removed", text=original))
        segments.append(DiffSegment(type="added", text=redraft))
    else:
        segments.append(DiffSegment(type="unchanged", text=original))
    
    return segments


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: UUID,
    user: User = Depends(get_current_active_subscriber),
    db: AsyncSession = Depends(get_db)
):
    """
    Get full article details including score, violations, and redraft.
    """
    result = await db.execute(
        select(Article)
        .options(
            joinedload(Article.outlet),
            joinedload(Article.topic)
        )
        .where(Article.id == article_id)
    )
    article = result.unique().scalar_one_or_none()
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Parse violations
    violations = parse_violations(article.violations)
    
    # Build redraft data if available
    redraft = None
    if article.redraft_body:
        redraft = ArticleRedraft(
            original_headline=article.headline,
            redraft_headline=article.redraft_headline or article.headline,
            original_body=article.body,
            redraft_body=article.redraft_body,
            headline_diff=create_diff_segments(
                article.headline,
                article.redraft_headline or article.headline,
                article.redraft_diff.get("headline") if article.redraft_diff else None
            ),
            body_diff=create_diff_segments(
                article.body,
                article.redraft_body,
                article.redraft_diff.get("body") if article.redraft_diff else None
            )
        )
    
    return ArticleResponse(
        id=article.id,
        headline=article.headline,
        body=article.body,
        url=article.url,
        author=article.author,
        published_at=article.published_at,
        score=article.score,
        violations=violations,
        redraft=redraft,
        outlet=OutletBrief.model_validate(article.outlet),
        topic=TopicResponse.model_validate(article.topic) if article.topic else None,
        scraped_at=article.scraped_at,
        scored_at=article.scored_at
    )
