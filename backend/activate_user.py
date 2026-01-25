
import asyncio
from app.db.database import AsyncSessionLocal
from sqlalchemy import select, update
from app.db.models import User

async def activate():
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.email == "test@example.com")
        user = (await db.execute(stmt)).scalar_one_or_none()
        
        if user:
            print(f"User found: {user.email}, Status: {user.subscription_status}")
            user.subscription_status = "active"
            await db.commit()
            print("Updated subscription to active.")
        else:
            print("User not found.")

if __name__ == "__main__":
    asyncio.run(activate())
