
import asyncio
from app.db.database import AsyncSessionLocal
from sqlalchemy import select
from app.db.models import MagicLink

async def get_link():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MagicLink).order_by(MagicLink.created_at.desc()).limit(1)
        )
        link = result.scalar_one_or_none()
        if link:
            with open("link_clean.txt", "w") as f:
                f.write(f"http://localhost:3000/auth/verify?token={link.token}")
            print("Wrote to link_clean.txt")
        else:
            print("No magic links found.")

if __name__ == "__main__":
    asyncio.run(get_link())
