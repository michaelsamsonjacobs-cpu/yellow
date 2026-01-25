"""
Firestore Sync Service

Mirrors data from Postgres (SQLAlchemy) to Firestore for frontend consumption.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from sqlalchemy.orm import Session
from typing import List
import json

from app.db.models import Article, Topic, Outlet
from app.config import get_settings

settings = get_settings()

# Initialize Firebase Admin
# We expect the Firebase Service Account JSON to be available or use default
try:
    if not firebase_admin._apps:
        # Check for service account file
        sa_path = "firebase-service-account.json"
        if os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to default or credentials from env if possible
            firebase_admin.initialize_app()
except Exception as e:
    print(f"Firestore Initialization Error: {e}")

db = None
try:
    db = firestore.client()
except:
    print("Could not get firestore client")

def sync_outlet_to_firestore(outlet: Outlet):
    """Sync a single outlet to Firestore"""
    if not db: return
    
    doc_ref = db.collection("outlets").document(str(outlet.id))
    doc_ref.set({
        "name": outlet.name,
        "domain": outlet.domain,
        "logo_url": outlet.logo_url,
        "batting_average": outlet.batting_average,
        "integrity_score": outlet.batting_average, # Compatibility
        "bias_tilt": outlet.bias_tilt,
        "total_articles": outlet.total_articles,
        "is_wire_service": outlet.is_wire_service,
        "last_updated": firestore.SERVER_TIMESTAMP
    }, merge=True)

def sync_topic_to_firestore(topic: Topic):
    """Sync a single topic to Firestore"""
    if not db: return
    
    doc_ref = db.collection("topics").document(str(topic.id))
    doc_ref.set({
        "name": topic.name,
        "slug": topic.slug,
        "region": "us" if topic.category == "us" else "international",
        "article_count": topic.article_count,
        "avg_score": topic.avg_score,
        "created_at": topic.created_at
    }, merge=True)

def sync_article_to_firestore(article: Article, outlet_name: str):
    """Sync a single article to Firestore"""
    if not db: return
    
    doc_ref = db.collection("articles").document(str(article.id))
    doc_ref.set({
        "topic_id": str(article.topic_id) if article.topic_id else None,
        "outlet_id": str(article.outlet_id),
        "outlet_name": outlet_name,
        "title": article.headline,
        "headline": article.headline, # Compatibility
        "original_text": article.body,
        "integrity_score": article.score or 0,
        "published_at": article.published_at,
        "scraped_at": article.scraped_at,
        "category_tag": article.category_tag,
        "redrafted_text": article.redraft_body,
        "diff_html": json.dumps(article.redraft_diff) if article.redraft_diff else None
    }, merge=True)

import os
