from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.states.result_submission_states import ResultSubmissionStates
from src.bot.utils.validators import validate_time_format, time_to_milliseconds
from src.services.calculation_service import (
	calculate_average_ao5,
	calculate_average_mean_of_3,
	calculate_best_of_3,
	get_best_time,
)
from src.database.database import get_session
from src.database.crud import competition as competition_crud
from src.database.crud import participant as participant_crud
from src.database.crud import user as user_crud
from src.database.crud import result as result_crud
from src.database.crud import discipline as discipline_crud
from src.services.leaderboard_service import calculate_discipline_leaderboard

router = Router()


@router.message(Command("submit_results"))
async def submit_results(message: Message, state: FSMContext) -> None:
	await state.set_state(ResultSubmissionStates.SelectDiscipline)
	await message.answer("Введите через пробел код соревнования и код дисциплины (например: ABCD1234 3x3):")


@router.message(StateFilter(ResultSubmissionStates.SelectDiscipline))
async def select_discipline(message: Message, state: FSMContext) -> None:
	parts = message.text.split()
	if len(parts) < 2:
		await message.answer("Неверный формат. Пример: ABCD1234 3x3")
		return
	code = parts[0].strip().upper()
	disc_code = parts[1].strip().lower()
	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if not comp:
			await message.answer("Соревнование с таким кодом не найдено.")
			return
		if comp.status == "completed":
			await message.answer("Это соревнование завершено организатором. Отправка результатов недоступна.")
			return
		disc_list = await discipline_crud.get_by_codes(session, [disc_code])
		if not disc_list:
			await message.answer("Дисциплина не найдена.")
			return
		disc = disc_list[0]
		await state.update_data(code=code, discipline_id=disc.id, discipline_attempts=disc.attempts_count, calc_type=disc.average_calculation_type)
	await state.set_state(ResultSubmissionStates.EnterResults)
	await message.answer(
		"Отправьте времена попыток в формате X.Y.Z или DNF, по одному через запятую.\n"
		"Пример для 5 попыток: 0.11.34, 0.12.10, 0.10.99, 0.13.50, 0.11.00"
	)


@router.message(StateFilter(ResultSubmissionStates.EnterResults))
async def enter_results(message: Message, state: FSMContext) -> None:
	data = await state.get_data()
	attempts_required: int = data["discipline_attempts"]
	calc_type: str = data["calc_type"]
	disc_id: int = data["discipline_id"]
	code: str = data["code"]

	items = [x.strip() for x in message.text.split(",") if x.strip()]
	if len(items) != attempts_required:
		await message.answer(f"Ожидалось {attempts_required} попыток, получено {len(items)}. Попробуйте снова.")
		return
	if not all(validate_time_format(x) for x in items):
		await message.answer("Обнаружен неверный формат времени. Попробуйте снова.")
		return
	attempts_ms = [time_to_milliseconds(x) for x in items]

	if calc_type == "ao5":
		average_ms, average_dnf = calculate_average_ao5(attempts_ms)
	elif calc_type == "mean_of_3":
		average_ms, average_dnf = calculate_average_mean_of_3(attempts_ms)
	else:
		average_ms, average_dnf = calculate_best_of_3(attempts_ms)
	best_ms = get_best_time(attempts_ms)

	async for session in get_session():
		comp = await competition_crud.get_by_code(session, code)
		if comp and comp.status == "completed":
			await message.answer("Это соревнование завершено организатором. Отправка результатов недоступна.")
			return
		u = await user_crud.get_by_telegram_id(session, message.from_user.id)  # type: ignore[arg-type]
		if not u:
			await message.answer("Сначала зарегистрируйтесь: /register")
			return
		p = await participant_crud.get(session, (comp.id if comp else 0), u.id)  # type: ignore[union-attr]
		if not p:
			await message.answer("Вы не зарегистрированы на это соревнование. Используйте /register.")
			return
		await result_crud.upsert_result(session, p.id, disc_id, attempts_ms, average_ms, average_dnf, best_ms)
		await session.commit()

	await message.answer("Результаты сохранены. Спасибо!")
	await state.clear()


@router.message(Command("my_results"))
async def my_results(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 2:
		await message.answer("Использование: /my_results <код_соревнования>")
		return
	code = parts[1].strip().upper()
	async for session in get_session():
		u = await user_crud.get_by_telegram_id(session, message.from_user.id)  # type: ignore[arg-type]
		comp = await competition_crud.get_by_code(session, code)
		if not u or not comp:
			await message.answer("Данные не найдены.")
			return
		p = await participant_crud.get(session, comp.id, u.id)
		if not p:
			await message.answer("Вы не зарегистрированы на это соревнование.")
			return
		# simple dump of results
		from sqlalchemy import select
		from src.database.models import Result, Discipline
		rows = await session.execute(
			select(Discipline.code, Result.average_time, Result.average_dnf, Result.best_time)
			.where(Result.participant_id == p.id)
			.join(Discipline, Discipline.id == Result.discipline_id)
		)
		lines = ["Ваши результаты:"]
		for r in rows:
			code, avg, dnf, best = r
			avg_s = "DNF" if dnf else _fmt(avg)
			best_s = _fmt(best) if best is not None else "—"
			lines.append(f"{code}: среднее={avg_s}, лучшая={best_s}")
		await message.answer("\n".join(lines))


@router.message(Command("my_position"))
async def my_position(message: Message) -> None:
	parts = (message.text or "").split()
	if len(parts) < 3:
		await message.answer("Использование: /my_position <код_соревнования> <код_дисциплины>")
		return
	code = parts[1].strip().upper()
	disc_code = parts[2].strip().lower()
	async for session in get_session():
		u = await user_crud.get_by_telegram_id(session, message.from_user.id)  # type: ignore[arg-type]
		comp = await competition_crud.get_by_code(session, code)
		if not u or not comp:
			await message.answer("Данные не найдены.")
			return
		d_list = await discipline_crud.get_by_codes(session, [disc_code])
		if not d_list:
			await message.answer("Дисциплина не найдена.")
			return
		data = await calculate_discipline_leaderboard(session, comp.id, d_list[0].id, store=False)
		# find user
		pos = next((it.get("position") for it in data if it["user_id"] == u.id), None)
		if not pos:
			await message.answer("Вы не в таблице лидеров по этой дисциплине (возможно, нет результата).")
			return
		await message.answer(f"Ваше место: {pos}")


def _fmt(ms: int | None) -> str:
	if ms is None:
		return "DNF"
	total_seconds, milli = divmod(ms, 1000)
	minutes, seconds = divmod(total_seconds, 60)
	centis = milli // 10
	if minutes:
		return f"{minutes}:{seconds:02d}.{centis:02d}"
	return f"{seconds}.{centis:02d}"
