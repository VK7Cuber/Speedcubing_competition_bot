from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
	EnterCompetitionCode = State()
	EnterFirstName = State()
	EnterLastName = State()
