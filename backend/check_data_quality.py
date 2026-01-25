
import asyncio
from app.db.database import AsyncSessionLocal
from sqlalchemy import func, select
from app.db.models import Article, Topic

async def check_quality():
    async with AsyncSessionLocal() as db:
        # Check total
        total = (await db.execute(select(func.count(Article.id)))).scalar()
        # Check scored
        scored = (await db.execute(select(func.count(Article.id)).where(Article.score != None))).scalar()
        
        # Check topics
        topics_count = (await db.execute(select(func.count(Topic.id)))).scalar()
        
        # Check articles with topics
        with_topic = (await db.execute(select(func.count(Article.id)).where(Article.topic_id != None))).scalar()
        
        # Sample topic names and dates
        topics = (await db.execute(select(Topic.name, Topic.date).limit(5))).all()

    with open("data_quality.txt", "w") as f:
        f.write(f"Total Articles: {total}\n")
        f.write(f"Scored Articles: {scored}\n")
        f.write(f"Total Topics: {topics_count}\n")
        f.write(f"Articles with Topic: {with_topic}\n")
        f.write(f"Sample Topics with Dates: {topics}\n")
    print("Wrote to data_quality.txt")

if __name__ == "__main__":
    asyncio.run(check_quality())
