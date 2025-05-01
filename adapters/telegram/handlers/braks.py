from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import dp
import re
from datetime import datetime
from adapters.database.repositories.defect_repository import DefectRepocitory
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from adapters.logs.logger import log_action
from adapters.telegram.fsm.all_state import Brack 



defect_repo = DefectRepocitory() #из репозитория берем наш класс



@dp.message_handler(Command('set_brack'))
async def defect(message: types.Message):
	await message.answer("Введите дату")
	await Brack.data_brack.set()




@dp.message_handler(state=Brack.data_brack)
async def defect_data(message: types.Message, state: FSMContext):
	text = message.text.strip() #текст пользователя без пробелов

	if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", text):
		await message.answer("Введите правильный формат даты: DD-MM-YYYY")
		return

	try:
		data_brack = datetime.strptime(text, "%d-%m-%Y") #преобразуем текст в объект даты
		await state.update_data(data_brack=data_brack.strftime("%d-%m-%Y"))#сохраняем в правильном формате
		await message.answer("Введите полное название устройства")
		await Brack.name_phone.set()
	except ValueError:
		await message.answer("Введите правильный формат даты: DD-MM-YYYY")
	
		

@dp.message_handler(state=Brack.name_phone)
async def defect_phone(message: types.Message, state: FSMContext):
	await state.update_data(name_phone=message.text)
	await message.answer("Введите город отправителя")
	await Brack.city.set()



@dp.message_handler(state=Brack.city)
async def defect_city(message: types.Message, state: FSMContext):
	await state.update_data(city=message.text)
	await message.answer("Введите имей устройства")
	await Brack.imei.set()



@dp.message_handler(state=Brack.imei)
async def defect_imei(message: types.Message, state: FSMContext):
	await state.update_data(imei=message.text)
	await message.answer("Введите состояние(проблему) устройства")
	await Brack.is_defect.set()


@dp.message_handler(state=Brack.is_defect)
async def defect_is(message: types.Message, state: FSMContext):
	await state.update_data(is_defect=message.text)
	await message.answer("Отправьте фотографию устройства")
	await Brack.photo_defect.set()



@dp.message_handler(content_types=[types.ContentType.PHOTO] , state=Brack.photo_defect)
async def defect_condition(message: types.Message, state: FSMContext):
	user_data = await state.get_data() #извлекаем наши состояния 
	user_id = message.from_user.id
	data_brack = user_data.get("data_brack")
	name_phone = user_data.get("name_phone")
	city = user_data.get("city")
	imei = user_data.get("imei")
	is_defect = user_data.get("is_defect")

	photo_defect = message.photo[-1].file_id #выбераем качество фото и присваиваем айди к файлу

	await defect_repo.register_defect(user_id, data_brack , name_phone, city, imei, is_defect, photo_defect)
	await message.answer("Ваш брак успешно зарегестрирован!")
	await state.finish()
	

@dp.message_handler(lambda message: message.content_type != types.ContentType.PHOTO, state=Brack.photo_defect)#если это не фото
async def invalid_photo_defect(message: types.Message):
	await message.answer("Это не фотография.")




@dp.message_handler(Command('braki'))
async def get_braki(message: types.Message):
	user_data = await defect_repo.get_all_braki(message.from_user.id)

	if not user_data:
		await message.answer("У вас еще нет браков")
		return

	data_brack , name_phone, city, imei, is_defect, photo_defect = user_data #получаем весь список

	text = (f"Принятые браки:\n\n"
			f"дата: {data_brack}\n"
			f"название устройства: {name_phone}\n"
			f"город отправителя: {city}\n"
			f"имей: {imei}\n"
			f"дефект устройства: {is_defect}")

	await message.answer_photo(photo=photo_defect, caption=text)



@dp.message_handler(Command('cancel'), state="*")
async def cancel_cmd_brack(message: types.Message , state: FSMContext):
	currant_state = await state.get_state()
	print(f"Текущие состояние: {currant_state}")
	if currant_state is None:
		await message.answer("У вас нет активного действия")
		return 

	await state.finish()
	await message.reply("Действие отменино")