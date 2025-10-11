import asyncio
from aiogram import Bot, Dispatcher
from loguru import logger

from src.config.settings import settings
from src.bot.handlers.start import router as start_router
from src.bot.handlers.organizer_handlers import router as organizer_router
from src.bot.handlers.participant_handlers import router as participant_router
from src.bot.handlers.results_handlers import router as results_router
from src.bot.handlers.competition_handlers import router as competition_router


dp = Dispatcher()

dp.include_router(start_router)

dp.include_router(organizer_router)

dp.include_router(participant_router)

dp.include_router(results_router)

dp.include_router(competition_router)


async def main() -> None:
	logger.remove()
	logger.add(lambda msg: print(msg, end=""), level=settings.log_level)
	bot = Bot(token=settings.bot_token)
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())

