from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from bot import dp , bot
from adapters.logs.logger import log_action
from aiogram.types import Message , SuccessfulPayment
from adapters.database.repositories.user_repository import UserRepository
from adapters.database.repositories.defect_repository import DefectRepocitory
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


user_repo = UserRepository()
defect_repo = DefectRepocitory()


help_text = """
<b>/donate</b> - покупка премиума 
<b>/logout</b> - выйти с аккаунта
<b>/set_brack</b> - зарегестрировать брак
<b>/set_success_brak</b> - зарегестрировать починку брака
<b>/braki</b> - список ваших браков
<b>/succes_braki</b> - список ваших починенных браков
<b>/cancel</b> - отмененить действие
<b>/kassa</b> - сформировать отчет
<b>/debt</b> - установить локальный долг"""



@dp.message_handler(Command('help'))
async def help_cmd(message: types.Message):
	await message.answer(help_text , parse_mode="HTML")




@dp.message_handler(Command('test_prem'))
async def test_prem_cmd(message: types.Message):
	if not await user_repo.is_premium(message.from_user.id):
		await message.answer("Эта функция доступна только с премиумом!")
		return
	await message.answer("Вы идеален)")



@dp.message_handler(Command('donate'))
async def send_invoice(message: types.Message):
	await bot.send_invoice(
	chat_id=message.from_user.id,
	title="Премиум",
	description="После покупки вам будет доступны команды kassa и debt и огромная благодарность)",
	payload="prenium_access", #это как каллбек
	provider_token="TelegramBotStars",
	currency="XTR",
	prices=[types.LabeledPrice(label="Премиум", amount=1 * 1)]

	)



@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
	await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)#подтверждение оплаты


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
	user_id = message.from_user.id
	
	await user_repo.set_premium(user_id , True) #Ставим статус чела с подпиской
	await message.answer("Спасибо за покупку!")





@dp.message_handler(Command('cancel'), state="*")
async def cancel_cmd(message: types.Message , state: FSMContext):
	currant_state = await state.get_state()
	print(f"Текущие состояние: {currant_state}")
	if currant_state is None:
		await message.answer("У вас нет активного действия")
		return 

	await state.finish()
	await message.reply("Действие отменино")

