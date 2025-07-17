"""Database session and engine setup.
Keeping it tiny and readable – like something you’d write on a quiet Sunday.
"""
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///./edtech.db"

# echo=True prints SQL queries for easier debugging when developing.
engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    """FastAPI dependency that yields an `AsyncSession`."""
    session: AsyncSession = async_session()
    try:
        yield session
    finally:
        await session.close()
