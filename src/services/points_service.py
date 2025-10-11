def calculate_points_for_discipline(position: int, total_participants: int, participants_with_dnf: int) -> int:
	# X = Y - N + 1, where Y = total_participants - participants_with_dnf
	Y = max(total_participants - participants_with_dnf, 0)
	if position <= 0 or position > Y:
		return 0
	return Y - position + 1


def calculate_overall_leaderboard(competition_id: int) -> None:
	# Will aggregate points per participant across disciplines
	return None


def get_overall_leaderboard(competition_id: int):
	return []
