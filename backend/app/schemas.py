"""
Pydantic Schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ============ Enums ============

class SubscriptionStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"


class TopicCategory(str, Enum):
    US = "us"
    INTL = "intl"


# ============ Auth Schemas ============

class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    message: str = "Check your email for the magic link"
    email: str


class VerifyTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class AuthMeResponse(BaseModel):
    user: "UserResponse"


# ============ User Schemas ============

class UserBase(BaseModel):
    email: EmailStr
    newsletter_opt_in: bool = False


class UserResponse(BaseModel):
    id: UUID
    email: str
    subscription_status: SubscriptionStatus
    newsletter_opt_in: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    newsletter_opt_in: Optional[bool] = None


class SubscribeResponse(BaseModel):
    checkout_url: str


class PortalResponse(BaseModel):
    portal_url: str


# ============ Topic Schemas ============

class TopicBase(BaseModel):
    name: str
    category: TopicCategory
    keywords: Optional[Dict[str, Any]] = None


class TopicResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    category: TopicCategory
    date: datetime
    article_count: int
    avg_score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class TopicListResponse(BaseModel):
    us_topics: List[TopicResponse]
    intl_topics: List[TopicResponse]
    date: datetime


class TopicDetailResponse(TopicResponse):
    keywords: Optional[Dict[str, Any]] = None


# ============ Article Schemas ============

class ViolationDetail(BaseModel):
    type: str
    description: str
    deduction: int
    instances: Optional[List[str]] = None


class ArticleBrief(BaseModel):
    id: UUID
    headline: str
    url: str
    score: Optional[int] = None
    outlet_name: str
    outlet_domain: str
    published_at: Optional[datetime] = None
    has_redraft: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class DiffSegment(BaseModel):
    type: str  # 'unchanged', 'removed', 'added'
    text: str


class ArticleRedraft(BaseModel):
    original_headline: str
    redraft_headline: str
    original_body: str
    redraft_body: str
    headline_diff: List[DiffSegment]
    body_diff: List[DiffSegment]


class ArticleResponse(BaseModel):
    id: UUID
    headline: str
    body: str
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    score: Optional[int] = None
    violations: Optional[List[ViolationDetail]] = None
    redraft: Optional[ArticleRedraft] = None
    outlet: "OutletBrief"
    topic: Optional["TopicResponse"] = None
    scraped_at: datetime
    scored_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    articles: List[ArticleBrief]
    total: int
    page: int
    page_size: int


# ============ Outlet Schemas ============

class OutletBrief(BaseModel):
    id: UUID
    name: str
    domain: str
    logo_url: Optional[str] = None
    batting_average: float
    
    model_config = ConfigDict(from_attributes=True)


class TopViolation(BaseModel):
    type: str
    percentage: float
    count: int


class OutletResponse(BaseModel):
    id: UUID
    name: str
    domain: str
    logo_url: Optional[str] = None
    batting_average: float
    bias_tilt: float  # -1 to +1
    total_articles: int
    monthly_visits: Optional[int] = None
    is_wire_service: bool
    top_violations: Optional[List[TopViolation]] = None
    
    model_config = ConfigDict(from_attributes=True)


class OutletHistoryPoint(BaseModel):
    date: datetime
    score: float
    article_count: int


class OutletHistoryResponse(BaseModel):
    outlet: OutletBrief
    history: List[OutletHistoryPoint]


class OutletListResponse(BaseModel):
    outlets: List[OutletBrief]
    total: int


# ============ Newsletter Schemas ============

class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr


class NewsletterSubscribeResponse(BaseModel):
    message: str = "Successfully subscribed to the newsletter"
    email: str


class NewsletterUnsubscribeRequest(BaseModel):
    token: str


class NewsletterUnsubscribeResponse(BaseModel):
    message: str = "Successfully unsubscribed from the newsletter"


# ============ Webhook Schemas ============

class StripeWebhookResponse(BaseModel):
    received: bool = True


# ============ Error Schemas ============

class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]]


# Update forward references
VerifyTokenResponse.model_rebuild()
AuthMeResponse.model_rebuild()
ArticleResponse.model_rebuild()
