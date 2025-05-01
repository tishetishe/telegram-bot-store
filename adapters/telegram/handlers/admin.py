from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp
from config import ADMINS
from utils import is_admin
from adapters.database.repositories.user_repository import UserRepository
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State , StatesGroup
from adapters.logs.logger import log_action
from adapters.telegram.keyboard.kb_admin import admin_keyboard_panel
from aiogram.types import InputFile #для работы с файлами на диске
from adapters.telegram.fsm.all_state import Mail 
from celery_app import send_mass_message , log_action



"""class Mail(StatesGroup):
	watch_text = State()"""
		


user_repo = UserRepository()


@dp.message_handler(Command('adminka'))
@is_admin #декоратор для проверки админки
async def admin_cmd(message: types.Message, state: FSMContext):
	#await log_action(message.from_user.id , "запускает админ-панель")
	await message.answer("🎛Добро пожаловать в админ-панель", reply_markup=admin_keyboard_panel())



@dp.message_handler(lambda message: message.text == "📋Логи")
@is_admin
async def send_logs(message: types.Message):
	try:

		log_file = InputFile("bot_logs.txt")#отправляем готовые файлы
		await message.answer_document(log_file, caption="📋Логи:")#присылаем логи
	except Exception as e:
		await message.answer(f"⚠️Ошибка: {e}")#если возникла ошибка



@dp.message_handler(lambda message: message.text == "📢Рассылка")
@is_admin
async def start_mailing(message: types.Message):
	await message.answer("📝Введите текст для рассылки:", reply_markup=admin_keyboard_panel())
	await Mail.watch_text.set()



@dp.message_handler(state=Mail.watch_text)#наше состояние для отправки
@is_admin
async def watch_text(message: types.Message, state: FSMContext):
	text = message.text #текст нашей будующей рассылки
	user_ids = await user_repo.get_all_users()#получаем всех наших пользователей


	send_mass_message.delay(user_ids , text)

	await message.answer(f"Рассылка запущена для {len(user_ids)} пользователей!")


	#send_count = 0 #успешиных рассылок
	#failed_count = 0 #неуспешных)))

	#for user in users:
	#	try:
	#		await dp.bot.send_message(user, text) #извликаем из кортежа user_id(число) и сообщение 
	#		send_count += 1 #если бот смог отправить
	#	except Exception as e:
	#		failed_count += 1 #если бот не смог отправить
			#print(f"{e}")

	#await message.answer(f"Рассылка заверщена!\n📥Отправлено: {send_count}\n⚠️Ошибок: {failed_count}")
	await state.finish()




@dp.message_handler(lambda message: message.text == "🚧Техработы")
@is_admin
async def toggle_maintenance(message: types.Message):
	status = not await user_repo.is_maintenance() #для того что бы менять режим(True/False)
	await user_repo.set_maintenance(status) #обновляет статус

	text = "Бот снова работает" if not status else "Бот переведен в режим технических работ"
	await message.answer(text)







@dp.message_handler(lambda message: message.text == "❌отмена", state="*")
async def cancel_cmd_admin(message: types.Message , state: FSMContext):
	currant_state = await state.get_state()
	#print(f"Текущие состояние: {currant_state}")
	if currant_state is None:
		await message.answer("У вас нет активного действия")
		return 

	await state.finish()
	await message.reply("Действие отменино")
