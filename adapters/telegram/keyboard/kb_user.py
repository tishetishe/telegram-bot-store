from aiogram.types import ReplyKeyboardMarkup , KeyboardButton , InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData



def user_keyboard() -> ReplyKeyboardMarkup:
	ukb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton("💬Отзывы")],
	[KeyboardButton("📞Поддержка")],
	[KeyboardButton("💰Наш прайс")],
	[KeyboardButton("🛒Покупка товаров из прайса")]
	],resize_keyboard=True)
	return ukb



def user_item() -> InlineKeyboardMarkup:
	ikb = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton("📦Отложить", callback_data="save_teh")],
		[InlineKeyboardButton("❌Отменить", callback_data="cancel_teh")]
	])
	return ikb



def user_debt() -> InlineKeyboardMarkup:
	iud = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton("+ долг", callback_data="plus_debt")],
		[InlineKeyboardButton("- долг", callback_data="minus_debt")]
	])
	return iud




def user_kassa() -> InlineKeyboardMarkup:
	iuk = InlineKeyboardMarkup(inline_keyboard=[
		[InlineKeyboardButton("➕Доход", callback_data='income')],
		[InlineKeyboardButton("➖Расход", callback_data='expense')],
		[InlineKeyboardButton("🏁Завершить", callback_data='end')]
	])
	return iuk