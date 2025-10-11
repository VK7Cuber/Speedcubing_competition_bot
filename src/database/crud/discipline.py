from typing import List, Dict, Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Discipline, CompetitionDiscipline


async def list_all(session: AsyncSession) -> List[Discipline]:
	rows = await session.scalars(select(Discipline).order_by(Discipline.id))
	return list(rows)


async def get_by_codes(session: AsyncSession, codes: Iterable[str]) -> List[Discipline]:
	codes_norm = [c.strip().lower() for c in codes if c and c.strip()]
	if not codes_norm:
		return []
	rows = await session.scalars(select(Discipline).where(Discipline.code.in_(codes_norm)))
	return list(rows)


def to_code_map(items: List[Discipline]) -> Dict[str, Discipline]:
	return {d.code.lower(): d for d in items}


async def list_by_competition(session: AsyncSession, competition_id: int) -> List[Discipline]:
	rows = await session.scalars(
		select(Discipline)
		.join(CompetitionDiscipline, CompetitionDiscipline.discipline_id == Discipline.id)
		.where(CompetitionDiscipline.competition_id == competition_id)
		.order_by(Discipline.id)
	)
	return list(rows)
