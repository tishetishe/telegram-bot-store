from aiogram.types import ReplyKeyboardMarkup , KeyboardButton , InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData



def admin_keyboard_panel() -> ReplyKeyboardMarkup:
	kb = ReplyKeyboardMarkup(keyboard=[
		[KeyboardButton("📋Логи")],
		[KeyboardButton("📢Рассылка")],
		[KeyboardButton("🚧Техработы")],
		[KeyboardButton("❌отмена")]
	],resize_keyboard=True) #что бы клавиатура рованой была
	return kb