from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Result


async def get_by_participant_and_discipline(session: AsyncSession, participant_id: int, discipline_id: int) -> Optional[Result]:
	return await session.scalar(
		select(Result).where(
			Result.participant_id == participant_id,
			Result.discipline_id == discipline_id,
		)
	)


async def upsert_result(
	session: AsyncSession,
	participant_id: int,
	discipline_id: int,
	attempts_ms: list[Optional[int]],
	average_ms: Optional[int],
	average_dnf: bool,
	best_ms: Optional[int],
) -> Result:
	res = await get_by_participant_and_discipline(session, participant_id, discipline_id)
	if res is None:
		res = Result(participant_id=participant_id, discipline_id=discipline_id)
		session.add(res)
	# assign attempts (pad to 5)
	vals = attempts_ms + [None] * (5 - len(attempts_ms))
	res.attempt_1_time = vals[0]
	res.attempt_1_dnf = vals[0] is None
	res.attempt_2_time = vals[1]
	res.attempt_2_dnf = vals[1] is None
	res.attempt_3_time = vals[2]
	res.attempt_3_dnf = vals[2] is None
	res.attempt_4_time = vals[3]
	res.attempt_4_dnf = vals[3] is None
	res.attempt_5_time = vals[4]
	res.attempt_5_dnf = vals[4] is None
	res.average_time = average_ms
	res.average_dnf = average_dnf
	res.best_time = best_ms
	await session.flush()
	return res
