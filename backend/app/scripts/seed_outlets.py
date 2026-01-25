"""
Seed Script - Initialize database with outlet data

Run with: python -m app.scripts.seed_outlets
"""
import asyncio
from app.db.database import AsyncSessionLocal
from app.db.models import Outlet
from app.scraper.outlets import OUTLET_CONFIGS


async def seed_outlets():
    """Seed database with all configured outlets"""
    async with AsyncSessionLocal() as db:
        for config in OUTLET_CONFIGS:
            # Check if exists
            from sqlalchemy import select
            result = await db.execute(
                select(Outlet).where(Outlet.domain == config.domain)
            )
            if result.scalar_one_or_none():
                print(f"Skipping {config.domain} (already exists)")
                continue
            
            outlet = Outlet(
                name=config.name,
                domain=config.domain,
                monthly_visits=config.monthly_visits,
                is_wire_service=config.is_wire_service,
                batting_average=0.0,
                bias_tilt=0.0
            )
            db.add(outlet)
            print(f"Added {config.name}")
        
        await db.commit()
        print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_outlets())
