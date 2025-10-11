from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.database.database import get_session
from src.database.crud import discipline as discipline_crud
from src.database.crud import competition as competition_crud
from src.services.leaderboard_service import (
	calculate_discipline_leaderboard,
	format_leaderboard_message,
	calculate_overall_leaderboard,
	format_overall_message,
)

router = Router()


@router.message(Command("leaderboard"))
async def leaderboard(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 3:
		await message.answer("Использование: /leaderboard <код_соревнования> <код_дисциплины>")
		return
	code = parts[1].strip().upper()
	disc_code = parts[2].strip().lower()
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование не найдено.")
			return
		disc = (await discipline_crud.get_by_codes(session, [disc_code]))
		if not disc:
			await message.answer("Дисциплина не найдена.")
			return
		data = await calculate_discipline_leaderboard(session, comp.id, disc[0].id, store=True)
		await session.commit()
		await message.answer(format_leaderboard_message(data))


@router.message(Command("overall"))
async def overall(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 2:
		await message.answer("Использование: /overall <код_соревнования>")
		return
	code = parts[1].strip().upper()
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование не найдено.")
			return
		items = await calculate_overall_leaderboard(session, comp.id, store=True)
		await session.commit()
		await message.answer(format_overall_message(items))
