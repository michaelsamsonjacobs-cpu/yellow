
import asyncio
from app.db.database import AsyncSessionLocal
from sqlalchemy import func, select
from app.db.models import Article

async def count():
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(func.count(Article.id)))
        print(f"Articles in DB: {r.scalar()}")

if __name__ == "__main__":
    asyncio.run(count())
