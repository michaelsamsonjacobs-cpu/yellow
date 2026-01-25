import asyncio
import sys
import os

# Add backend directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import AsyncSessionLocal
from app.db.models import Article, Topic, Outlet
from sqlalchemy import select, func

async def main():
    async with AsyncSessionLocal() as db:
        article_count = await db.execute(select(func.count(Article.id)))
        topic_count = await db.execute(select(func.count(Topic.id)))
        outlet_count = await db.execute(select(func.count(Outlet.id)))
        
        print(f"Articles: {article_count.scalar()}")
        print(f"Topics: {topic_count.scalar()}")
        print(f"Outlets: {outlet_count.scalar()}")

if __name__ == "__main__":
    asyncio.run(main())
