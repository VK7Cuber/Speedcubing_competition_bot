from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
	return await session.scalar(select(User).where(User.telegram_id == telegram_id))


async def create_user(session: AsyncSession, telegram_id: int, first_name: str, last_name: str, username: Optional[str] = None, role: str = "participant") -> User:
	user = User(
		telegram_id=telegram_id,
		username=username,
		first_name=first_name,
		last_name=last_name,
		role=role,
	)
	session.add(user)
	await session.flush()
	return user


async def get_or_create_participant_user(session: AsyncSession, telegram_id: int, first_name: str, last_name: str, username: Optional[str]) -> User:
	user = await get_by_telegram_id(session, telegram_id)
	if user:
		return user
	return await create_user(session, telegram_id, first_name, last_name, username, role="participant")
