from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def role_selection_kb() -> InlineKeyboardBuilder:
	kb = InlineKeyboardBuilder()
	kb.row(
		InlineKeyboardButton(text="Организатор", callback_data="role:organizer"),
		InlineKeyboardButton(text="Участник", callback_data="role:participant"),
	)
	return kb


def confirm_kb(text_ok: str = "Подтвердить", text_cancel: str = "Отмена") -> InlineKeyboardBuilder:
	kb = InlineKeyboardBuilder()
	kb.row(
		InlineKeyboardButton(text=text_ok, callback_data="confirm:ok"),
		InlineKeyboardButton(text=text_cancel, callback_data="confirm:cancel"),
	)
	return kb
