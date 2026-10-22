from db.base import engine, Base, async_session
from db.models import Lesson
import asyncio
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


if __name__ == "__main__":
    asyncio.run(init_models())

    exit(0)
