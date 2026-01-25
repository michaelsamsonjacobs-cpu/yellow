"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), unique=True),
        sa.Column('subscription_status', sa.String(50), default='inactive'),
        sa.Column('subscription_id', sa.String(255)),
        sa.Column('newsletter_opt_in', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('token', sa.String(512), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('ix_sessions_token', 'sessions', ['token'])
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])

    # Magic Links table
    op.create_table(
        'magic_links',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('token', sa.String(512), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('used', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('ix_magic_links_token', 'magic_links', ['token'])
    op.create_index('ix_magic_links_email', 'magic_links', ['email'])

    # Outlets table
    op.create_table(
        'outlets',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('domain', sa.String(255), unique=True, nullable=False),
        sa.Column('logo_url', sa.Text),
        sa.Column('batting_average', sa.Float, default=0.0),
        sa.Column('bias_tilt', sa.Float, default=0.0),
        sa.Column('total_articles', sa.Integer, default=0),
        sa.Column('monthly_visits', sa.Integer),
        sa.Column('is_wire_service', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.CheckConstraint('bias_tilt >= -1 AND bias_tilt <= 1', name='check_bias_range'),
    )
    op.create_index('ix_outlets_domain', 'outlets', ['domain'])

    # Topics table
    op.create_table(
        'topics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('category', sa.String(10), nullable=False),
        sa.Column('keywords', sa.JSON),
        sa.Column('date', sa.DateTime, nullable=False),
        sa.Column('article_count', sa.Integer, default=0),
        sa.Column('avg_score', sa.Float),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.CheckConstraint("category IN ('us', 'intl')", name='check_category'),
    )
    op.create_index('ix_topics_slug', 'topics', ['slug'])
    op.create_index('ix_topics_date', 'topics', ['date'])
    op.create_index('ix_topics_date_category', 'topics', ['date', 'category'])

    # Articles table
    op.create_table(
        'articles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('outlet_id', UUID(as_uuid=True), sa.ForeignKey('outlets.id')),
        sa.Column('topic_id', UUID(as_uuid=True), sa.ForeignKey('topics.id')),
        sa.Column('headline', sa.Text, nullable=False),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('url', sa.Text, unique=True, nullable=False),
        sa.Column('author', sa.String(255)),
        sa.Column('published_at', sa.DateTime),
        sa.Column('score', sa.Integer),
        sa.Column('violations', sa.JSON),
        sa.Column('redraft_headline', sa.Text),
        sa.Column('redraft_body', sa.Text),
        sa.Column('redraft_diff', sa.JSON),
        sa.Column('scraped_at', sa.DateTime, default=sa.func.now()),
        sa.Column('scored_at', sa.DateTime),
        sa.Column('embedding_id', sa.String(255)),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='check_score_range'),
    )
    op.create_index('ix_articles_url', 'articles', ['url'])
    op.create_index('ix_articles_outlet_id', 'articles', ['outlet_id'])
    op.create_index('ix_articles_topic_id', 'articles', ['topic_id'])
    op.create_index('ix_articles_outlet_score', 'articles', ['outlet_id', 'score'])
    op.create_index('ix_articles_scraped_at', 'articles', ['scraped_at'])

    # Newsletter Subscribers table
    op.create_table(
        'newsletter_subscribers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('unsubscribe_token', sa.String(255), unique=True, nullable=False),
        sa.Column('source', sa.String(50), default='website'),
        sa.Column('subscribed_at', sa.DateTime, default=sa.func.now()),
        sa.Column('unsubscribed_at', sa.DateTime),
    )
    op.create_index('ix_newsletter_email', 'newsletter_subscribers', ['email'])

    # Scoring Audits table
    op.create_table(
        'scoring_audits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('article_id', UUID(as_uuid=True), sa.ForeignKey('articles.id', ondelete='CASCADE')),
        sa.Column('initial_score', sa.Integer, default=100),
        sa.Column('final_score', sa.Integer),
        sa.Column('verification_score', sa.Integer, default=40),
        sa.Column('neutrality_score', sa.Integer, default=30),
        sa.Column('fairness_score', sa.Integer, default=20),
        sa.Column('violations_detail', sa.JSON),
        sa.Column('model_used', sa.String(50)),
        sa.Column('processed_at', sa.DateTime, default=sa.func.now()),
        sa.Column('processing_time_ms', sa.Integer),
    )
    op.create_index('ix_scoring_audits_article_id', 'scoring_audits', ['article_id'])


def downgrade() -> None:
    op.drop_table('scoring_audits')
    op.drop_table('newsletter_subscribers')
    op.drop_table('articles')
    op.drop_table('topics')
    op.drop_table('outlets')
    op.drop_table('magic_links')
    op.drop_table('sessions')
    op.drop_table('users')
