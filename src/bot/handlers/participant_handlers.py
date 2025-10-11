from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto

from src.bot.states.registration_states import RegistrationStates
from src.database.database import get_session
from src.database.crud import user as user_crud
from src.database.crud import competition as competition_crud
from src.database.crud import participant as participant_crud
from src.database.crud import discipline as discipline_crud
from src.database.crud import scramble as scramble_crud

router = Router()


@router.message(Command("view_competition_disciplines"))
async def view_competition_disciplines(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 2:
		await message.answer("Использование: /view_competition_disciplines <код_соревнования>")
		return
	code = parts[1].strip().upper()
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование не найдено.")
			return
		disciplines = await discipline_crud.list_by_competition(session, comp.id)
		if not disciplines:
			await message.answer("В соревновании нет дисциплин.")
			return
		text = "Дисциплины соревнования:\n" + "\n".join(f"- {d.name} ({d.code})" for d in disciplines)
		await message.answer(text)


@router.message(Command("register"))
async def register(message: Message, state: FSMContext) -> None:
	await state.set_state(RegistrationStates.EnterCompetitionCode)
	await message.answer("Введите код соревнования:")


@router.message(StateFilter(RegistrationStates.EnterCompetitionCode), F.text.len() > 0)
async def register_code(message: Message, state: FSMContext) -> None:
	code = message.text.strip().upper()
	await state.update_data(code=code)
	await state.set_state(RegistrationStates.EnterFirstName)
	await message.answer("Введите имя:")


@router.message(StateFilter(RegistrationStates.EnterFirstName), F.text.len() > 0)
async def register_first_name(message: Message, state: FSMContext) -> None:
	await state.update_data(first_name=message.text.strip())
	await state.set_state(RegistrationStates.EnterLastName)
	await message.answer("Введите фамилию:")


@router.message(StateFilter(RegistrationStates.EnterLastName), F.text.len() > 0)
async def register_last_name(message: Message, state: FSMContext) -> None:
	data = await state.get_data()
	code: str = data.get("code")
	first_name: str = data.get("first_name")
	last_name = message.text.strip()

	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование с таким кодом не найдено. Повторите регистрацию: /register")
			await state.clear()
			return
		u = await user_crud.get_or_create_participant_user(
			session,
			telegram_id=message.from_user.id,  # type: ignore[arg-type]
			first_name=first_name,
			last_name=last_name,
			username=message.from_user.username if message.from_user else None,  # type: ignore[attr-defined]
		)
		p = await participant_crud.get(session, comp.id, u.id)
		if not p:
			await participant_crud.create(session, comp.id, u.id)
		await session.commit()

	await message.answer("Регистрация завершена. Удачи в соревнованиях!")
	await state.clear()


@router.message(Command("get_scrambles"))
async def get_scrambles(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 3:
		await message.answer("Использование: /get_scrambles <код_соревнования> <код_дисциплины>")
		return
	code = parts[1].strip().upper()
	disc_code = parts[2].strip().lower()
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование не найдено.")
			return
		d_list = await discipline_crud.get_by_codes(session, [disc_code])
		if not d_list:
			await message.answer("Дисциплина не найдена.")
			return
		scrambles = await scramble_crud.list_by_competition_discipline(session, comp.id, d_list[0].id)
		if not scrambles:
			await message.answer("Скрамблы ещё не загружены организатором.")
			return
		if len(scrambles) == 1:
			await message.answer_photo(scrambles[0].file_id, caption=f"Скрамблы для {disc_code}")
			return
		media = [InputMediaPhoto(media=s.file_id) for s in scrambles]
		await message.answer_media_group(media)
