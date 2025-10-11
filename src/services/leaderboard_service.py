from typing import Any, List, Dict, Tuple

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
	User,
	Participant,
	Result,
	Leaderboard,
	OverallLeaderboard,
)
from src.services.points_service import calculate_points_for_discipline


async def calculate_discipline_leaderboard(
	session: AsyncSession,
	competition_id: int,
	discipline_id: int,
	store: bool = True,
) -> List[Dict[str, Any]]:
	rows = await session.execute(
		select(
			User.id.label("user_id"),
			User.first_name,
			User.last_name,
			Result.average_time,
			Result.average_dnf,
			Result.best_time,
		)
		.join(Participant, Participant.user_id == User.id)
		.join(Result, Result.participant_id == Participant.id)
		.where(
			Participant.competition_id == competition_id,
			Result.discipline_id == discipline_id,
		)
	)
	items = [dict(r._mapping) for r in rows]
	# count non-DNF for points later
	non_dnf_count = sum(1 for it in items if not it["average_dnf"])
	# sort: DNF last; otherwise by average_time asc; tiebreak by best_time asc
	def sort_key(it: Dict[str, Any]) -> Tuple[int, int | float, int | float]:
		if it["average_dnf"]:
			return (1, float("inf"), float("inf"))
		avg = it["average_time"] if it["average_time"] is not None else 10**12
		best = it["best_time"] if it["best_time"] is not None else 10**12
		return (0, avg, best)

	items.sort(key=sort_key)
	# assign positions and points
	for idx, it in enumerate(items, start=1):
		it["position"] = idx if not it["average_dnf"] else None
		it["points"] = 0 if it["average_dnf"] else calculate_points_for_discipline(idx, len(items), len(items) - non_dnf_count)

	if store:
		# clear old rows and insert new
		await session.execute(
			delete(Leaderboard).where(
				Leaderboard.competition_id == competition_id,
				Leaderboard.discipline_id == discipline_id,
			)
		)
		for it in items:
			lb = Leaderboard(
				competition_id=competition_id,
				discipline_id=discipline_id,
				user_id=it["user_id"],
				position=it["position"] or 0,
				average_time=it["average_time"],
				average_dnf=it["average_dnf"],
				best_time=it["best_time"],
				points=it["points"],
			)
			session.add(lb)
		await session.flush()
	return items


async def calculate_overall_leaderboard(
	session: AsyncSession,
	competition_id: int,
	store: bool = True,
) -> List[Dict[str, Any]]:
	# Sum points from Leaderboard per user
	rows = await session.execute(
		select(
			User.id.label("user_id"),
			User.first_name,
			User.last_name,
		)
		.join(Participant, Participant.user_id == User.id)
		.where(Participant.competition_id == competition_id)
	)
	participants = {r.user_id: {"user_id": r.user_id, "first_name": r.first_name, "last_name": r.last_name, "total_points": 0, "disciplines_participated": 0} for r in rows}
	lb_rows = await session.execute(
		select(Leaderboard.user_id, Leaderboard.points).where(Leaderboard.competition_id == competition_id)
	)
	for r in lb_rows:
		u = participants.get(r.user_id)
		if not u:
			continue
		u["total_points"] += r.points
		u["disciplines_participated"] += 1
	items = list(participants.values())
	items.sort(key=lambda x: x["total_points"], reverse=True)
	for idx, it in enumerate(items, start=1):
		it["position"] = idx

	if store:
		await session.execute(delete(OverallLeaderboard).where(OverallLeaderboard.competition_id == competition_id))
		for it in items:
			ol = OverallLeaderboard(
				competition_id=competition_id,
				user_id=it["user_id"],
				total_points=it["total_points"],
				disciplines_participated=it["disciplines_participated"],
				position=it["position"],
			)
			session.add(ol)
		await session.flush()
	return items


def format_leaderboard_message(leaderboard_data: List[Dict[str, Any]]) -> str:
	lines = ["Таблица лидеров:"]
	for it in leaderboard_data:
		name = f"{it['first_name']} {it['last_name']}".strip()
		avg = "DNF" if it["average_dnf"] else _fmt(it["average_time"])  # type: ignore[arg-type]
		best = _fmt(it["best_time"]) if it["best_time"] is not None else "—"
		pos = it["position"] if it["position"] else "—"
		lines.append(f"{pos}. {name}  среднее: {avg}  лучшая: {best}  баллы: {it['points']}")
	return "\n".join(lines)


def format_overall_message(items: List[Dict[str, Any]]) -> str:
	lines = ["Общий зачёт:"]
	for it in items:
		name = f"{it['first_name']} {it['last_name']}".strip()
		lines.append(f"{it['position']}. {name}  баллы: {it['total_points']}  дисциплин: {it['disciplines_participated']}")
	return "\n".join(lines)


def _fmt(ms: int | None) -> str:
	if ms is None:
		return "DNF"
	total_seconds, milli = divmod(ms, 1000)
	minutes, seconds = divmod(total_seconds, 60)
	centis = milli // 10
	if minutes:
		return f"{minutes}:{seconds:02d}.{centis:02d}"
	return f"{seconds}.{centis:02d}"
