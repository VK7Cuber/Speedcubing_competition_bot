from src.services.calculation_service import (
	calculate_average_ao5,
	calculate_average_mean_of_3,
	calculate_best_of_3,
	get_best_time,
)


def test_ao5_no_dnf():
	attempts = [5120, 5780, 4980, 6540, 6000]  # ms
	avg, dnf = calculate_average_ao5(attempts)
	assert not dnf
	# drop best 4980 and worst 6540, average 5120+5780+6000 = 16900 / 3 = 5633ms
	assert avg == 5633


def test_ao5_one_dnf():
	attempts = [5120, 5780, 4980, 6540, None]
	avg, dnf = calculate_average_ao5(attempts)
	assert not dnf
	# drop DNF and drop best 4980, average 5120+5780+6540 = 17440 / 3 = 5813ms
	assert avg == 5813


def test_ao5_two_dnf():
	attempts = [5120, None, 4980, None, 6000]
	avg, dnf = calculate_average_ao5(attempts)
	assert dnf
	assert avg is None


def test_mean_of_3():
	attempts = [1000, 2000, 3000]
	avg, dnf = calculate_average_mean_of_3(attempts)
	assert not dnf and avg == 2000


def test_mean_of_3_with_dnf():
	attempts = [1000, None, 3000]
	avg, dnf = calculate_average_mean_of_3(attempts)
	assert dnf and avg is None


def test_best_of_3():
	attempts = [3000, 2000, 2500]
	avg, dnf = calculate_best_of_3(attempts)
	assert not dnf and avg == 2000


def test_best_of_3_all_dnf():
	attempts = [None, None, None]
	avg, dnf = calculate_best_of_3(attempts)
	assert dnf and avg is None


def test_get_best_time():
	attempts = [3000, None, 1500, 2500]
	assert get_best_time(attempts) == 1500
