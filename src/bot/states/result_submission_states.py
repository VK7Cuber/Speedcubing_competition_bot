from aiogram.fsm.state import State, StatesGroup


class ResultSubmissionStates(StatesGroup):
	SelectDiscipline = State()
	EnterResults = State()
