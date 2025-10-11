from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardBuilder:
	kb = ReplyKeyboardBuilder()
	kb.row(KeyboardButton(text="Меню"))
	return kb
