from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config.settings import settings


class Base(DeclarativeBase):
	pass


engine = create_async_engine(
	settings.database_url,
	echo=False,
	pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
	engine,
	expire_on_commit=False,
	class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
	async with AsyncSessionLocal() as session:
		yield session

