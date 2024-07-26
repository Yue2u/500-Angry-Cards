from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings


# Postgresql
engine = create_async_engine(settings.DB_URL, echo=False, future=True)
LocalAsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with LocalAsyncSession() as session:
        yield session
