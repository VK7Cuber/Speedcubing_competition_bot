import secrets
import string
from typing import Optional, Sequence, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Competition, CompetitionDiscipline


_CODE_ALPHABET = string.ascii_uppercase + string.digits


def _generate_code(length: int = 8) -> str:
	return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))


async def create_competition(session: AsyncSession, name: str, organizer_id: int) -> Competition:
	code = _generate_code(8)
	while await session.scalar(select(Competition).where(Competition.competition_code == code)):
		code = _generate_code(8)
	comp = Competition(name=name, organizer_id=organizer_id, competition_code=code, status="active")
	session.add(comp)
	await session.flush()
	return comp


async def add_disciplines(session: AsyncSession, competition_id: int, discipline_ids: Sequence[int]) -> None:
	# fetch existing
	existing = await session.scalars(
		select(CompetitionDiscipline.discipline_id).where(CompetitionDiscipline.competition_id == competition_id)
	)
	existing_set = set(existing)
	for d_id in discipline_ids:
		if d_id in existing_set:
			continue
		session.add(CompetitionDiscipline(competition_id=competition_id, discipline_id=d_id, is_active=True))
	await session.flush()


async def get_by_code(session: AsyncSession, code: str) -> Optional[Competition]:
	return await session.scalar(select(Competition).where(Competition.competition_code == code))


async def list_by_organizer(session: AsyncSession, organizer_id: int) -> List[Competition]:
	rows = await session.scalars(select(Competition).where(Competition.organizer_id == organizer_id).order_by(Competition.created_at.desc()))
	return list(rows)


async def complete_competition(session: AsyncSession, competition_id: int) -> None:
	await session.execute(
		update(Competition).where(Competition.id == competition_id).values(status="completed")
	)
	await session.flush()
