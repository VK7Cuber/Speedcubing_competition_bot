from typing import Optional


def format_time(ms: Optional[int]) -> str:
	if ms is None:
		return "DNF"
	total_seconds, milli = divmod(ms, 1000)
	minutes, seconds = divmod(total_seconds, 60)
	centis = milli // 10
	if minutes:
		return f"{minutes}:{seconds:02d}.{centis:02d}"
	return f"{seconds}.{centis:02d}"


def format_participant_name(first_name: str, last_name: str) -> str:
	return f"{first_name} {last_name}".strip()
