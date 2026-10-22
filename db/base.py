from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/lessons"

engine = create_async_engine(DATABASE_URL)
Base = declarative_base()

# Используем async_sessionmaker вместо sessionmaker
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
