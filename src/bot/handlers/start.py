from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
	await message.answer(
		"Привет! Я Speedcubing Competition Bot. Используй /help, чтобы узнать команды."
	)


@router.message(Command("help"))
async def help_cmd(message: Message) -> None:
	await message.answer(
		"Доступные команды:\n"
		"/start — приветствие\n"
		"/help — список команд\n"
		"/view_competition_disciplines — список дисциплин соревнования\n"
		"/create_competition — создать соревнование (организатор)\n"
		"/my_competitions — мои соревнования (организатор)\n"
		"/competition_info — информация о соревновании (организатор)\n"
		"/add_disciplines — добавить дисциплины (организатор)\n"
		"/complete_competition — завершить соревнование (организатор)\n"
		"/register — регистрация в соревновании (участник)\n"
		"/get_scrambles — получить скрамблы по дисциплине (участник)\n"
		"/submit_results — отправить результаты (участник)\n"
		"/my_results — мои результаты (участник)\n"
		"/my_position — моё место в дисциплине (участник)\n"
		"/leaderboard — таблица лидеров по дисциплине\n"
		"/overall — общий зачёт\n"
	)
