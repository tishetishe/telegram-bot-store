from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import dp
import re
from datetime import datetime
from adapters.database.repositories.defect_repository import DefectRepocitory
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from adapters.logs.logger import log_action
from adapters.telegram.fsm.all_state import SBrack


defect_repo = DefectRepocitory()



@dp.message_handler(Command('set_success_brak'))
async def success_brak_cmd(message: types.Message):
	await message.answer("Введите дату починеного брака")
	await SBrack.data_bs.set()



@dp.message_handler(state=SBrack.data_bs)
async def data_bs_cmd(message: types.Message, state: FSMContext):
	text = message.text.strip() #текст пользователя

	if not re.fullmatch(r'\d{2}-\d{2}-\d{4}', text):
		await message.answer("Введите коректную дату DD-MM-YYYY") 
		return #проверяет на шаблон

	try:
		data_bs = datetime.strptime(text, "%d-%m-%Y") #преобразовывает в объект дататайм(типо 2024, 5, 12 , 0 , 0)
		await state.update_data(data_bs=data_bs.strftime("%d-%m-%Y"))#сохраняем в правильном формате(12-05-2024)
		await message.answer("Введите полное название устройства")
		await SBrack.phone_bs.set() #нью состояние
	except ValueError:
		await message.answer("Введите правильный формат даты: DD-MM-YYYY") #если пользователь ввел что-то кроме чисел



@dp.message_handler(state=SBrack.phone_bs)
async def success_brak_phone(message: types.Message, state: FSMContext):
	await message.answer("Введите город")
	await state.update_data(phone_bs=message.text)
	await SBrack.city_bs.set()



@dp.message_handler(state=SBrack.city_bs)
async def success_brak_city(message: types.Message, state: FSMContext):
	await message.answer("Введите имей устройства")
	await state.update_data(city_bs=message.text)
	await SBrack.imei_bs.set()



@dp.message_handler(state=SBrack.imei_bs)
async def success_brak_imei(message: types.Message, state: FSMContext):
	await message.answer("Введите накладную СДЕК")
	await state.update_data(imei_bs=message.text)
	await SBrack.CDEK.set()




@dp.message_handler(state=SBrack.CDEK)
async def success_brak_CDEK(message: types.Message, state: FSMContext):
	if not message.text.isdigit():
		await message.answer("Введите номер накладной!")
		return

	user_id = message.from_user.id
	user_data = await state.get_data() #получаем все состояния
	data_bs = user_data.get("data_bs")
	phone_bs = user_data.get("phone_bs")
	city_bs = user_data.get("city_bs")
	imei_bs = user_data.get("imei_bs")
	CDEK = message.text


	await defect_repo.succes_defect(user_id, data_bs, phone_bs, city_bs, imei_bs, CDEK) #записываем в базу данных
	await message.answer("Ваш отремонтированный брак был зарегестрирован!")
	await state.finish()
	


@dp.message_handler(Command('succes_braki'))
async def success_braki_cmd(message: types.Message):
	user_data = await defect_repo.get_success_braki(message.from_user.id)

	if not user_data:
		await message.answer("У вас нет еще отправленных браков")
		return

	data_bs, phone_bs, city_bs, imei_bs, CDEK = user_data

	text=(f"Отправленные браки\n\n"
		  f"дата: {data_bs}\n"
		  f"устройство: {phone_bs}\n"
		  f"город: {city_bs}\n"
		  f"имей: {imei_bs}"
		  f"накладная СДЕК: {CDEK}")

	await message.answer(text)





@dp.message_handler(Command('cancel'), state="*")
async def cancel_cmd_brack(message: types.Message , state: FSMContext):
	currant_state = await state.get_state()
	print(f"Текущие состояние: {currant_state}")
	if currant_state is None:
		await message.answer("У вас нет активного действия")
		return 

	await state.finish()
	await message.reply("Действие отменино")