from sqlalchemy import select, func
import asyncio
import os

DATABASE_URL = "postgresql+asyncpg://postgres:lUpZHBfatIOdRZtv@db.kpvdoeabrsfqqzpmthpc.supabase.co:5432/postgres"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid

class Base(DeclarativeBase): pass

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

async def main():
    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        a_count = await session.execute(select(func.count(Article.id)))
        t_count = await session.execute(select(func.count(Topic.id)))
        print(f"COUNT_ARTICLES: {a_count.scalar()}")
        print(f"COUNT_TOPICS: {t_count.scalar()}")

if __name__ == "__main__":
    asyncio.run(main())
