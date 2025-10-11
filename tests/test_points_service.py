from src.services.points_service import calculate_points_for_discipline


def test_points_basic():
	# 15 participants, 2 DNF => Y=13
	assert calculate_points_for_discipline(1, 15, 2) == 13
	assert calculate_points_for_discipline(2, 15, 2) == 12
	assert calculate_points_for_discipline(3, 15, 2) == 11


def test_points_out_of_range():
	# position out of non-DNF range -> 0
	assert calculate_points_for_discipline(14, 15, 2) == 0
	assert calculate_points_for_discipline(0, 10, 0) == 0
