from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.states.competition_states import CompetitionStates
from src.database.database import get_session
from src.database.crud import competition as competition_crud
from src.database.crud import discipline as discipline_crud
from src.database.crud import user as user_crud
from src.database.crud import scramble as scramble_crud

router = Router()


@router.message(Command("my_competitions"))
async def my_competitions(message: Message) -> None:
	async for session in get_session():
		u = await user_crud.get_by_telegram_id(session, message.from_user.id)  # type: ignore[arg-type]
		if not u:
			await message.answer("У вас пока нет соревнований.")
			return
		rows = await competition_crud.list_by_organizer(session, u.id)
		if not rows:
			await message.answer("У вас пока нет соревнований.")
			return
		text = "Ваши соревнования:\n" + "\n".join(f"- {c.name} (код: {c.competition_code}, статус: {c.status})" for c in rows)
		await message.answer(text)


@router.message(Command("add_disciplines"))
async def add_disciplines_cmd(message: Message, state: FSMContext) -> None:
	parts = (message.text or "").split(maxsplit=2)
	if len(parts) < 3:
		await message.answer("Использование: /add_disciplines <код_соревнования> <коды_через_запятую>")
		return
	code = parts[1].strip().upper()
	codes = [c.strip().lower() for c in parts[2].split(",") if c.strip()]
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование не найдено.")
			return
		if comp.status == "completed":
			await message.answer("Соревнование завершено. Добавление дисциплин недоступно.")
			return
		disc = await discipline_crud.get_by_codes(session, codes)
		if not disc:
			await message.answer("Дисциплины не распознаны.")
			return
		# filter out already added
		existing = await discipline_crud.list_by_competition(session, comp.id)
		existing_codes = {d.code.lower() for d in existing}
		new_disciplines = [d for d in disc if d.code.lower() not in existing_codes]
		dup_disciplines = [d for d in disc if d.code.lower() in existing_codes]
		if dup_disciplines:
			dup_list = ", ".join(f"{d.name} ({d.code})" for d in dup_disciplines)
			await message.answer(f"Эти дисциплины уже добавлены и будут пропущены: {dup_list}")
		if not new_disciplines:
			await message.answer("Новые дисциплины для добавления не найдены.")
			return
		await competition_crud.add_disciplines(session, comp.id, [d.id for d in new_disciplines])
		await session.commit()
	# immediately start upload flow for newly added disciplines
	d_queue = [(d.id, d.code, d.attempts_count) for d in new_disciplines]
	await state.update_data(comp_code=comp.competition_code, comp_id=comp.id, upload_queue=d_queue, creation_flow=False)
	await _prompt_next_upload(message, state)


@router.message(Command("complete_competition"))
async def complete_competition_cmd(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 2:
		await message.answer("Использование: /complete_competition <код_соревнования>")
		return
	code = parts[1].strip().upper()
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование не найдено.")
			return
		await competition_crud.complete_competition(session, comp.id)
		await session.commit()
		await message.answer("Соревнование помечено как завершённое.")


@router.message(Command("create_competition"))
async def create_competition(message: Message, state: FSMContext) -> None:
	await state.set_state(CompetitionStates.EnterCompetitionName)
	await message.answer("Введите название соревнования:")


@router.message(StateFilter(CompetitionStates.EnterCompetitionName))
async def comp_enter_name(message: Message, state: FSMContext) -> None:
	name = message.text.strip()
	await state.update_data(name=name)
	await state.set_state(CompetitionStates.SelectDisciplines)
	await message.answer(
		"Введите коды дисциплин через запятую (например: 2x2,3x3,skewb,clock).\n"
		"Список дисциплин смотрите в Documentation/List_of_WCA_disciplines.md"
	)


@router.message(StateFilter(CompetitionStates.SelectDisciplines))
async def comp_select_disciplines(message: Message, state: FSMContext) -> None:
	codes = [c.strip().lower() for c in message.text.split(",") if c.strip()]
	data = await state.get_data()
	name: str = data.get("name")
	async for session in get_session():
		u = await user_crud.get_by_telegram_id(session, message.from_user.id)  # type: ignore[arg-type]
		if not u:
			u = await user_crud.create_user(
				session,
				telegram_id=message.from_user.id,  # type: ignore[arg-type]
				first_name=message.from_user.first_name or "",
				last_name=message.from_user.last_name or "",
				username=message.from_user.username if message.from_user else None,
				role="organizer",
			)
		disciplines = await discipline_crud.get_by_codes(session, codes)
		if not disciplines:
			await message.answer("Не удалось распознать дисциплины. Отмена.")
			await session.rollback()
			await state.clear()
			return
		comp = await competition_crud.create_competition(session, name=name, organizer_id=u.id)
		await competition_crud.add_disciplines(session, comp.id, [d.id for d in disciplines])
		await session.commit()
	# prepare upload queue
	d_queue = [(d.id, d.code, d.attempts_count) for d in disciplines]
	await state.update_data(comp_code=comp.competition_code, comp_id=comp.id, upload_queue=d_queue, creation_flow=True)
	await _prompt_next_upload(message, state)


async def _prompt_next_upload(message: Message, state: FSMContext) -> None:
	data = await state.get_data()
	upload_queue = data.get("upload_queue", [])
	if not upload_queue:
		comp_code = data.get("comp_code")
		if data.get("creation_flow", False):
			await message.answer(
				f"Соревнование создано и скрамблы загружены! Готово.\nКод соревнования: {comp_code}"
			)
		else:
			await message.answer("Отлично! Дисциплины успешно добавлены.")
		await state.clear()
		return
	d_id, d_code, attempts = upload_queue[0]
	await state.set_state(CompetitionStates.UploadSpecificDiscipline)
	await message.answer(
		f"Загрузите {attempts} фото скрамблов для дисциплины {d_code}.\n"
		"Отправьте одним сообщением все фото по очереди."
	)


@router.message(StateFilter(CompetitionStates.UploadSpecificDiscipline), F.photo)
async def comp_upload_scrambles(message: Message, state: FSMContext) -> None:
	data = await state.get_data()
	upload_queue = list(data.get("upload_queue", []))
	comp_id: int = data["comp_id"]
	d_id, d_code, attempts = upload_queue[0]
	photos = message.photo
	# accept only when multiple photos exist: Telegram sends sizes for a single photo; we need file_id of highest quality per photo
	# Organizer should send exactly 'attempts' photos as separate media group ideally, but to simplify: we accept last size as best for this message
	# If fewer photos than required, ask to re-send
	if len(photos) < 1:
		await message.answer("Не удалось получить фото. Повторите отправку.")
		return
	# store a single photo per message as attempt next-in-order; if multiple attempts needed, organizer should send attempts по одному сообщению
	# Determine next attempt number from DB
	async for session in get_session():
		existing = await scramble_crud.list_by_competition_discipline(session, comp_id, d_id)
		next_attempt = len(existing) + 1
		if next_attempt > attempts:
			await message.answer("Все скрамблы для этой дисциплины уже загружены. Отправьте следующий.")
			return
		file_id = photos[-1].file_id
		await scramble_crud.upsert_scramble(session, comp_id, d_id, next_attempt, file_id)
		await session.commit()
		if next_attempt == attempts:
			# move queue
			upload_queue.pop(0)
			await state.update_data(upload_queue=upload_queue)
			await message.answer(f"Скрамблы для {d_code} загружены.")
			await _prompt_next_upload(message, state)
		else:
			await message.answer(f"Скрамбл {next_attempt}/{attempts} сохранён. Отправьте следующий.")


@router.message(Command("competition_info"))
async def competition_info(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 2:
		await message.answer("Использование: /competition_info <код>")
		return
	code = parts[1].strip().upper()
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование не найдено.")
			return
		await message.answer(f"Соревнование: {comp.name}\nСтатус: {comp.status}\nКод: {comp.competition_code}")
