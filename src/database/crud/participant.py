from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Participant


async def get(session: AsyncSession, competition_id: int, user_id: int) -> Optional[Participant]:
	return await session.scalar(
		select(Participant).where(
			Participant.competition_id == competition_id,
			Participant.user_id == user_id,
		)
	)


async def create(session: AsyncSession, competition_id: int, user_id: int) -> Participant:
	p = Participant(competition_id=competition_id, user_id=user_id)
	session.add(p)
	await session.flush()
	return p
