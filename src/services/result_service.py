from typing import Optional, Sequence

from src.bot.utils.validators import validate_time_format, time_to_milliseconds


def save_result(participant_id: int, discipline_id: int, attempts: Sequence[str]) -> None:
	# Placeholder: validation only
	for v in attempts:
		if not validate_time_format(v):
			raise ValueError("Неверный формат времени")
		_ = time_to_milliseconds(v)
	return None


def update_result(result_id: int, attempts: Sequence[str]) -> None:
	for v in attempts:
		if not validate_time_format(v):
			raise ValueError("Неверный формат времени")
	return None


def get_participant_results(participant_id: int, competition_id: int):
	return []
