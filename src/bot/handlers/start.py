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
		"\n"
		"Общие:\n"
		"/start — запуск бота, приветствие\n"
		"/help — список команд\n"
		"/view_all_WCA_disciplines — показать все доступные дисциплины WCA и их коды\n"
		"\n"
		"Организаторам:\n"
		"/create_competition — создать соревнование\n"
		"/my_competitions — мои соревнования\n"
		"/competition_info — информация о соревновании\n"
		"/add_disciplines — добавить дисциплины\n"
		"/complete_competition — завершить соревнование\n"
		"\n"
		"Участникам:\n"
		"/register — регистрация на соревнование\n"
		"/get_scrambles — получить скрамблы по конкретной дисциплине\n"
		"/submit_results — отправить результаты\n"
		"/my_results — мои результаты\n"
		"/my_position — моё место в дисциплине\n"
		"/leaderboard — таблица лидеров по дисциплине\n"
		"/overall — общий зачёт\n"
		"/view_competition_disciplines — список дисциплин соревнования\n"
	)
