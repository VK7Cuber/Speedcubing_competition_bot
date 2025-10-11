import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.disciplines_config import DISCIPLINES
from src.database.database import AsyncSessionLocal
from src.database.models import Discipline


async def seed() -> None:
	async with AsyncSessionLocal() as session:  # type: AsyncSession
		for d in DISCIPLINES:
			exists = await session.scalar(select(Discipline).where(Discipline.code == d["code"]))
			if exists:
				continue
			db = Discipline(
				name=d["name"],
				code=d["code"],
				attempts_count=d["attempts_count"],
				average_calculation_type=d["average_calculation_type"],
				dnf_threshold=d["dnf_threshold"],
				max_time_minutes=d["max_time_minutes"],
			)
			session.add(db)
		await session.commit()


if __name__ == "__main__":
	asyncio.run(seed())
