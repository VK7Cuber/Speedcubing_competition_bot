from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Scramble


async def upsert_scramble(
	session: AsyncSession,
	competition_id: int,
	discipline_id: int,
	attempt_number: int,
	file_id: str,
	file_path: Optional[str] = None,
) -> Scramble:
	existing = await session.scalar(
		select(Scramble).where(
			Scramble.competition_id == competition_id,
			Scramble.discipline_id == discipline_id,
			Scramble.attempt_number == attempt_number,
		)
	)
	if existing:
		existing.file_id = file_id
		existing.file_path = file_path
		await session.flush()
		return existing
	s = Scramble(
		competition_id=competition_id,
		discipline_id=discipline_id,
		attempt_number=attempt_number,
		file_id=file_id,
		file_path=file_path,
	)
	session.add(s)
	await session.flush()
	return s


async def list_by_competition_discipline(
	session: AsyncSession,
	competition_id: int,
	discipline_id: int,
) -> List[Scramble]:
	rows = await session.scalars(
		select(Scramble).where(
			Scramble.competition_id == competition_id,
			Scramble.discipline_id == discipline_id,
		).order_by(Scramble.attempt_number)
	)
	return list(rows)
