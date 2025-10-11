from aiogram.fsm.state import State, StatesGroup


class CompetitionStates(StatesGroup):
	EnterCompetitionName = State()
	SelectDisciplines = State()
	UploadScrambles = State()
	UploadSpecificDiscipline = State()
