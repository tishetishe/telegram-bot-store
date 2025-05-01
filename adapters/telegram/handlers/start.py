#команда старт
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.handler import CancelHandler #отменить выполнения обработчика
from aiogram.dispatcher.middlewares import BaseMiddleware
from bot import dp , bot
from adapters.logs.logger import log_action
from utils import is_admin
from adapters.database.repositories.user_repository import UserRepository
import os
from config import ADMINS
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from adapters.telegram.keyboard.kb_start import reg_log_mark
from adapters.telegram.keyboard.kb_user import user_keyboard 
import bcrypt
from adapters.telegram.fsm.all_state import AuthOrRegister



user_repo = UserRepository()


@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
	await log_action(message.from_user.id , "запустил бота")
	await message.answer("Добро пожаловать!\nЯ бот для покупки и продажи товаров\nВыберите Действие:",reply_markup=reg_log_mark())
	



@dp.callback_query_handler(lambda x: x.data in ['log' , 'reg'])
async def register_or_login(call: types.CallbackQuery, state: FSMContext):
	user_id = call.from_user.id
	user_exists = await user_repo.user_exists(user_id) #проверка пользователя на регестрацию

	if call.data == 'log':
		if not user_exists:
			await call.message.answer("Вы еще не зарегались")
			return
		await call.message.answer("Введите свой логин")
		await AuthOrRegister.auth_login.set()

	elif call.data == 'reg':
		if user_exists:
			await call.message.answer("Вы уже зарегестрированы", reply_markup=user_keyboard())
			return
		await call.message.answer("Придумайте логин")
		await AuthOrRegister.register_login_user.set()

	await call.answer()




@dp.message_handler(state=AuthOrRegister.register_login_user)
async def register_login_cmd(message: types.Message, state: FSMContext):
	login = message.text.strip()#переменная с логином(без пробелов)

	if len(login) < 5:
		await message.answer("Логин должен быть длинее 5 символов")
		return #если меньше 5 символов, то ошибка

	elif await user_repo.is_login_take(login):
		await message.answer("Этот никнейм уже занят!")
		return

	await state.update_data(login=login) #в состоянии создаем переменную 
	await message.answer("Теперь придумайте пароль")
	await AuthOrRegister.register_password_user.set()




@dp.message_handler(state=AuthOrRegister.register_password_user)
async def register_password_cmd(message: types.Message, state: FSMContext):
	user_data = await state.get_data()#получаем дананные
	login = user_data.get("login") #извлекаем данные из переменной
	password = message.text.strip() #пароль берем из сообщения юзера
	user_id = message.from_user.id #получем айдишник

	if len(password) < 5:
		await message.answer("Пароль должен быть длинее 5 символов")
		return

	await user_repo.register_login(user_id, login) #записываем логин

	hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()) #encode -> переводит в байты. gensalt -> создает соль.pashpw -> делает хэш пароля
	await user_repo.register_password(user_id, hashed_password) #записываем пароль
	

	await user_repo.set_authenticated(user_id, True) #тру у нас как 1(т.е вошел в акк)
	await message.answer("Вы успешно зарегались!\nВведите /help для списка команд" , reply_markup=user_keyboard())
	await state.finish()




@dp.message_handler(state=AuthOrRegister.auth_login)
async def auth_login_cmd(message: types.Message , state: FSMContext):
	user_id = message.from_user.id
	user_data = await user_repo.login(user_id)

	if not user_data:
		await message.answer("Неверный логин.")
		await suser_repo.set_authenticated(user_id, False)
		return

	save_login = user_data[0] 
	entered_login = message.text


	if entered_login != save_login:
		await message.answer("Вы ввели неверный логин")
		await user_repo.set_authenticated(user_id, False)
		return


	await state.update_data(login=user_data[0])#сохраняем логин(из бд) во временные данные
	await message.answer("Введите свой пароль")
	await AuthOrRegister.auth_password.set()




@dp.message_handler(state=AuthOrRegister.auth_password)
async def auth_password_cmd(message: types.Message , state: FSMContext):
	user_id = message.from_user.id
	user_data = await user_repo.login(user_id)

	if not user_data:
		await message.answer("Неверный пароль.")
		await user_repo.set_authenticated(user_id, False)
		return

	save_login = user_data[0] #логин из бд
	save_password = user_data[1] #пароль из бд
	entered_password = message.text #пароль введенный юзером


	if not bcrypt.checkpw(entered_password.encode(), save_password):
		await message.answer("Вы ввели неверный пароль")
		await user_repo.set_authenticated(user_id, False)#хуярим 0, ибо он неверно ввел
		return

	await user_repo.set_authenticated(user_id, True) #тру у нас как 1(т.е вошел в акк)
	await message.answer("Вы успешно зашли в свой аккаунт!",reply_markup=user_keyboard())
	await state.finish()




@dp.message_handler(Command('logout'))
async def logout_cmd(message: types.Message):
	user_id = message.from_user.id
	await user_repo.set_authenticated(user_id, False) #фолс - 0, т.е вышел из акка
	await message.answer("Вы вышли из аккаунта")




@dp.message_handler(Command('cancel'), state="*")
async def cancel_cmd_start(message: types.Message , state: FSMContext):
	currant_state = await state.get_state()
	print(f"Текущие состояние: {currant_state}")
	if currant_state is None:
		await message.answer("У вас нет активного действия")
		return 

	await state.finish()
	await message.reply("Действие отменино")


