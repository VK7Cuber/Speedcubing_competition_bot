from src.bot.utils.validators import validate_time_format, time_to_milliseconds


def test_validate_time_ok():
	assert validate_time_format("0.11.34")
	assert validate_time_format("10.59.99")
	assert validate_time_format("DNF")


def test_validate_time_bad():
	assert not validate_time_format("1:23.45")
	assert not validate_time_format("abc")
	assert not validate_time_format("12.34")


def test_time_to_ms():
	assert time_to_milliseconds("0.11.34") == (11 * 1000 + 340)
	assert time_to_milliseconds("1.00.00") == 60000
	assert time_to_milliseconds("DNF") is None
	# minutes > 10 -> DNF
	assert time_to_milliseconds("11.00.00") is None
