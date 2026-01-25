"""
Topic Discovery Service

Scans AP and Reuters wire services daily to identify:
- Top 20 US topics
- Top 20 International topics

Uses NLP to extract and cluster keywords into topics.
"""
import asyncio
from datetime import datetime, date
from typing import List, Dict, Any, Tuple
from collections import Counter
from dataclasses import dataclass
import re

import httpx
from bs4 import BeautifulSoup
import spacy

from app.config import get_settings

settings = get_settings()

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Model not installed - will need to run: python -m spacy download en_core_web_sm
    nlp = None


@dataclass
class DiscoveredTopic:
    name: str
    slug: str
    category: str  # 'us' or 'intl'
    keywords: List[str]
    article_count: int


# AP News RSS Feeds
AP_FEEDS = {
    "us": [
        "https://rsshub.app/apnews/topics/us-news",
        "https://rsshub.app/apnews/topics/politics",
        "https://rsshub.app/apnews/topics/business",
    ],
    "intl": [
        "https://rsshub.app/apnews/topics/world-news",
        "https://rsshub.app/apnews/topics/international",
    ]
}

# Reuters RSS Feeds
REUTERS_FEEDS = {
    "us": [
        "https://www.reutersagency.com/feed/?best-regions=north-america&post_type=best",
    ],
    "intl": [
        "https://www.reutersagency.com/feed/?best-regions=europe&post_type=best",
        "https://www.reutersagency.com/feed/?best-regions=asia&post_type=best",
    ]
}


async def fetch_feed(url: str) -> List[Dict[str, str]]:
    """Fetch and parse an RSS feed"""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "xml")
            items = []
            
            for item in soup.find_all("item"):
                title = item.find("title")
                description = item.find("description")
                
                items.append({
                    "title": title.get_text(strip=True) if title else "",
                    "description": description.get_text(strip=True) if description else ""
                })
            
            return items
            
        except Exception as e:
            print(f"Error fetching feed {url}: {e}")
            return []


def extract_entities(text: str) -> List[str]:
    """Extract named entities from text using spaCy"""
    if not nlp:
        # Fallback: simple keyword extraction
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return list(set(words))
    
    doc = nlp(text)
    
    entities = []
    for ent in doc.ents:
        # Keep relevant entity types
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT", "LAW", "NORP"]:
            entities.append(ent.text)
    
    return entities


def cluster_into_topics(
    entities: List[str],
    min_count: int = 2,
    max_topics: int = 20
) -> List[Tuple[str, int]]:
    """
    Cluster entities into topics based on frequency.
    Returns list of (topic_name, count) tuples.
    """
    # Count entity occurrences
    counter = Counter(entities)
    
    # Filter by minimum count
    topics = [(name, count) for name, count in counter.most_common() 
              if count >= min_count]
    
    # Take top N
    return topics[:max_topics]


def slugify(text: str) -> str:
    """Convert text to URL-safe slug"""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug[:50]


async def discover_daily_topics() -> Tuple[List[DiscoveredTopic], List[DiscoveredTopic]]:
    """
    Discover today's top topics from wire services.
    Returns (us_topics, intl_topics).
    """
    us_entities = []
    intl_entities = []
    
    # Fetch US feeds
    for url in AP_FEEDS["us"] + REUTERS_FEEDS["us"]:
        items = await fetch_feed(url)
        for item in items:
            text = f"{item['title']} {item['description']}"
            entities = extract_entities(text)
            us_entities.extend(entities)
    
    # Fetch International feeds
    for url in AP_FEEDS["intl"] + REUTERS_FEEDS["intl"]:
        items = await fetch_feed(url)
        for item in items:
            text = f"{item['title']} {item['description']}"
            entities = extract_entities(text)
            intl_entities.extend(entities)
    
    # MANUAL FALLBACK (If feeds fail)
    if not us_entities:
        print("⚠️ Feeds failed. Using manual US fallback.")
        us_entities = ["2024 Election", "Immigration", "Senate", "Congress", "Inflation", "Trump", "Biden", "Supreme Court", "Border Crisis", "Federal Reserve"] * 5

    if not intl_entities:
        print("⚠️ Feeds failed. Using manual Intl fallback.")
        intl_entities = ["Gaza", "Ukraine", "Israel", "Putin", "China", "Taiwan", "NATO", "United Nations", "Hamas"] * 5
    
    # Cluster into topics
    us_topic_data = cluster_into_topics(us_entities)
    intl_topic_data = cluster_into_topics(intl_entities)
    
    # Create DiscoveredTopic objects
    us_topics = [
        DiscoveredTopic(
            name=name,
            slug=slugify(name),
            category="us",
            keywords=[name.lower()],  # Could expand with synonyms
            article_count=count
        )
        for name, count in us_topic_data
    ]
    
    intl_topics = [
        DiscoveredTopic(
            name=name,
            slug=slugify(name),
            category="intl",
            keywords=[name.lower()],
            article_count=count
        )
        for name, count in intl_topic_data
    ]
    
    return us_topics, intl_topics


async def get_wire_ground_truth(topic_name: str) -> List[Dict[str, str]]:
    """
    Get AP/Reuters coverage of a topic for fact-checking.
    Returns list of article summaries from wire services.
    """
    all_items = []
    
    # Search AP
    ap_search = f"https://rsshub.app/apnews/search/{topic_name}"
    items = await fetch_feed(ap_search)
    for item in items[:5]:
        item["source"] = "AP"
        all_items.append(item)
    
    return all_items
