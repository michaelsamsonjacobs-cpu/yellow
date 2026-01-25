"""
SQLAlchemy Models for Yellow
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, 
    ForeignKey, JSON, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    subscription_status: Mapped[str] = mapped_column(String(50), default="inactive")
    subscription_id: Mapped[Optional[str]] = mapped_column(String(255))
    newsletter_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships
    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """User sessions for auth"""
    __tablename__ = "sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")


class MagicLink(Base):
    """Passwordless magic links"""
    __tablename__ = "magic_links"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Outlet(Base):
    """News outlets being monitored"""
    __tablename__ = "outlets"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text)
    batting_average: Mapped[float] = mapped_column(Float, default=0.0)
    bias_tilt: Mapped[float] = mapped_column(Float, default=0.0)  # -1 (left) to +1 (right)
    total_articles: Mapped[int] = mapped_column(Integer, default=0)
    monthly_visits: Mapped[Optional[int]] = mapped_column(Integer)  # For ranking
    is_wire_service: Mapped[bool] = mapped_column(Boolean, default=False)  # AP, Reuters
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships
    articles: Mapped[List["Article"]] = relationship(back_populates="outlet")
    
    __table_args__ = (
        CheckConstraint('bias_tilt >= -1 AND bias_tilt <= 1', name='check_bias_range'),
    )


class Topic(Base):
    """Daily news topics (Top 20 US + Top 20 Intl)"""
    __tablename__ = "topics"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(10), nullable=False)  # 'us' or 'intl'
    keywords: Mapped[Optional[dict]] = mapped_column(JSON)  # Extracted keywords
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_score: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    articles: Mapped[List["Article"]] = relationship(back_populates="topic")
    
    __table_args__ = (
        CheckConstraint("category IN ('us', 'intl')", name='check_category'),
        Index('ix_topics_date_category', 'date', 'category'),
    )


class Article(Base):
    """Scraped and scored articles"""
    __tablename__ = "articles"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    outlet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("outlets.id"),
        index=True
    )
    topic_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("topics.id"),
        index=True
    )
    
    # Original content
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    author: Mapped[Optional[str]] = mapped_column(String(255))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Scoring
    score: Mapped[Optional[int]] = mapped_column(Integer)  # 0-100
    violations: Mapped[Optional[dict]] = mapped_column(JSON)  # Detailed breakdown
    
    # Redraft (if score < 70)
    redraft_headline: Mapped[Optional[str]] = mapped_column(Text)
    redraft_body: Mapped[Optional[str]] = mapped_column(Text)
    redraft_diff: Mapped[Optional[dict]] = mapped_column(JSON)  # For diff view
    
    # Metadata
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    scored_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255))  # Pinecone vector ID
    
    # Relationships
    outlet: Mapped["Outlet"] = relationship(back_populates="articles")
    topic: Mapped[Optional["Topic"]] = relationship(back_populates="articles")
    
    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 100', name='check_score_range'),
        Index('ix_articles_outlet_score', 'outlet_id', 'score'),
        Index('ix_articles_scraped_at', 'scraped_at'),
    )


class NewsletterSubscriber(Base):
    """Newsletter subscribers (may not be app users)"""
    __tablename__ = "newsletter_subscribers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    unsubscribe_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="website")  # website, app, etc.
    subscribed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class ScoringAudit(Base):
    """Audit log of scoring decisions for transparency"""
    __tablename__ = "scoring_audits"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("articles.id", ondelete="CASCADE"),
        index=True
    )
    
    # Scoring breakdown
    initial_score: Mapped[int] = mapped_column(Integer, default=100)
    final_score: Mapped[int] = mapped_column(Integer)
    
    # Category scores
    verification_score: Mapped[int] = mapped_column(Integer, default=40)
    neutrality_score: Mapped[int] = mapped_column(Integer, default=30)
    fairness_score: Mapped[int] = mapped_column(Integer, default=20)
    
    # Detailed violations
    violations_detail: Mapped[dict] = mapped_column(JSON)
    
    # AI processing info
    model_used: Mapped[str] = mapped_column(String(50))
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processing_time_ms: Mapped[int] = mapped_column(Integer)
