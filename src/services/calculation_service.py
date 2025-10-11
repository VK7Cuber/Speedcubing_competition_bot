from typing import Optional, Sequence


def get_best_time(attempts_ms: Sequence[Optional[int]]) -> Optional[int]:
	valid = [t for t in attempts_ms if t is not None]
	return min(valid) if valid else None


def calculate_average_ao5(attempts_ms: Sequence[Optional[int]]) -> tuple[Optional[int], bool]:
	# Ao5 rules (Documentation/List_of_WCA_disciplines.md):
	# - If 2+ DNF → average DNF
	# - If 1 DNF → drop that DNF (as the worst) and drop ONE best among valid; average remaining 3
	# - If 0 DNF → drop ONE best and ONE worst among 5; average remaining 3
	dnf_count = sum(1 for t in attempts_ms if t is None)
	if dnf_count >= 2:
		return None, True
	valid = [t for t in attempts_ms if t is not None]
	if len(valid) < 3:
		return None, True
	# Copy for safe removals
	vals = valid.copy()
	# remove ONE best
	best = min(vals)
	vals.remove(best)
	if dnf_count == 0:
		# remove ONE worst only when no DNF present
		worst = max(vals)
		vals.remove(worst)
	# now we should have exactly 3 values
	if len(vals) != 3:
		# Fallback: if something off, mark DNF to avoid incorrect scoring
		return None, True
	avg = sum(vals) // 3
	return avg, False


def calculate_average_mean_of_3(attempts_ms: Sequence[Optional[int]]) -> tuple[Optional[int], bool]:
	# If any DNF => average DNF
	if any(t is None for t in attempts_ms):
		return None, True
	avg = sum(attempts_ms) // 3  # type: ignore[arg-type]
	return avg, False


def calculate_best_of_3(attempts_ms: Sequence[Optional[int]]) -> tuple[Optional[int], bool]:
	best = get_best_time(attempts_ms)
	return (None, True) if best is None else (best, False)
