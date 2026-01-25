"""
Vector Database Service - Pinecone Integration

Stores article embeddings for:
1. Historical context retrieval (RAG)
2. Consistency scoring (how outlet covered similar topics before)
3. Topic clustering and similarity
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib
from pinecone import Pinecone
from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()

# Initialize clients
pc = Pinecone(api_key=settings.pinecone_api_key)
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Get or create index
INDEX_NAME = settings.pinecone_index


def get_index():
    """Get Pinecone index"""
    return pc.Index(INDEX_NAME)


async def create_embedding(text: str) -> List[float]:
    """Create embedding for text using OpenAI"""
    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks for embedding.
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within the chunk
            for i in range(end, start + chunk_size // 2, -1):
                if text[i] in '.!?\n':
                    end = i + 1
                    break
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks


async def store_article(
    article_id: str,
    headline: str,
    body: str,
    outlet_domain: str,
    topic_slug: str,
    published_at: datetime,
    score: Optional[int] = None
) -> List[str]:
    """
    Store article in vector database.
    Returns list of vector IDs.
    """
    index = get_index()
    
    # Combine headline and body for context
    full_text = f"{headline}\n\n{body}"
    
    # Chunk the text
    chunks = chunk_text(full_text)
    
    vector_ids = []
    vectors = []
    
    for i, chunk in enumerate(chunks):
        # Create unique ID for this chunk
        chunk_id = f"{article_id}_{i}"
        vector_ids.append(chunk_id)
        
        # Create embedding
        embedding = await create_embedding(chunk)
        
        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "article_id": article_id,
                "chunk_index": i,
                "outlet_domain": outlet_domain,
                "topic_slug": topic_slug,
                "published_at": published_at.isoformat(),
                "score": score,
                "text": chunk[:500]  # Store truncated text for reference
            }
        })
    
    # Upsert to Pinecone
    if vectors:
        index.upsert(vectors=vectors)
    
    return vector_ids


async def query_historical_context(
    headline: str,
    outlet_domain: str,
    top_k: int = 5,
    exclude_article_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Query for historical context - how this outlet covered similar topics.
    Used for consistency scoring.
    """
    index = get_index()
    
    # Create embedding for the query
    query_embedding = await create_embedding(headline)
    
    # Build filter - same outlet, different article
    filters = {"outlet_domain": {"$eq": outlet_domain}}
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k * 2,  # Get more to filter
        filter=filters,
        include_metadata=True
    )
    
    # Filter out the current article and dedupe by article_id
    seen_articles = set()
    context = []
    
    for match in results.get("matches", []):
        article_id = match["metadata"].get("article_id")
        
        if article_id == exclude_article_id:
            continue
        if article_id in seen_articles:
            continue
            
        seen_articles.add(article_id)
        
        context.append({
            "article_id": article_id,
            "text": match["metadata"].get("text", ""),
            "score": match["metadata"].get("score"),
            "published_at": match["metadata"].get("published_at"),
            "similarity": match["score"]
        })
        
        if len(context) >= top_k:
            break
    
    return context


async def query_similar_coverage(
    topic_slug: str,
    headline: str,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Find similar articles across all outlets for a topic.
    Used for cross-outlet comparison.
    """
    index = get_index()
    
    # Create embedding
    query_embedding = await create_embedding(headline)
    
    # Query with topic filter
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"topic_slug": {"$eq": topic_slug}},
        include_metadata=True
    )
    
    # Dedupe by article
    seen = set()
    coverage = []
    
    for match in results.get("matches", []):
        article_id = match["metadata"].get("article_id")
        if article_id in seen:
            continue
        seen.add(article_id)
        
        coverage.append({
            "article_id": article_id,
            "outlet_domain": match["metadata"].get("outlet_domain"),
            "text": match["metadata"].get("text", ""),
            "score": match["metadata"].get("score"),
            "similarity": match["score"]
        })
    
    return coverage


async def delete_article_vectors(article_id: str) -> None:
    """Delete all vectors for an article"""
    index = get_index()
    
    # Pinecone doesn't support metadata filtering for delete,
    # so we need to know the vector IDs
    # In practice, store vector_ids in the Article model
    
    # For now, assume max 5 chunks per article
    vector_ids = [f"{article_id}_{i}" for i in range(5)]
    index.delete(ids=vector_ids)


def format_context_for_scoring(context: List[Dict[str, Any]]) -> str:
    """Format historical context for the scoring prompt"""
    if not context:
        return ""
    
    lines = ["Previous coverage by this outlet:"]
    for item in context[:3]:  # Top 3 most similar
        score = item.get("score")
        score_str = f" (Score: {score}/100)" if score else ""
        lines.append(f"- {item['text'][:200]}...{score_str}")
    
    return "\n".join(lines)
