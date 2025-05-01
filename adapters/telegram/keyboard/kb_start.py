from aiogram.types import ReplyKeyboardMarkup , KeyboardButton , InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData



def reg_log_mark() -> InlineKeyboardMarkup:
	rlm = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton("Войти", callback_data="log")],
		[InlineKeyboardButton("Зарегестрироваться", callback_data="reg")]
	])
	return rlm