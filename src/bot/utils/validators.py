import re
from typing import Optional

_TIME_RE = re.compile(r"^(?P<m>\d{1,2})\.(?P<s>\d{1,2})\.(?P<cs>\d{1,2})$")


def validate_time_format(value: str) -> bool:
	if value.strip().upper() == "DNF":
		return True
	m = _TIME_RE.match(value.strip())
	if not m:
		return False
	minutes = int(m.group("m"))
	seconds = int(m.group("s"))
	centis = int(m.group("cs"))
	if minutes > 10:
		return True  # трактуем как валидный ввод, но логически будет DNF при конвертации
	return 0 <= seconds < 60 and 0 <= centis <= 99


def time_to_milliseconds(value: str) -> Optional[int]:
	value = value.strip().upper()
	if value == "DNF":
		return None
	m = _TIME_RE.match(value)
	if not m:
		return None
	minutes = int(m.group("m"))
	seconds = int(m.group("s"))
	centis = int(m.group("cs"))
	if minutes > 10:
		return None
	return (minutes * 60 + seconds) * 1000 + centis * 10
