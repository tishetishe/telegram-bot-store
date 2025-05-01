from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from adapters.database.repositories.user_repository import UserRepository
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.storage import FSMContext
from bot import Dispatcher
from adapters.telegram.handlers.start import AuthOrRegister
from adapters.telegram.keyboard.kb_user import user_keyboard


class AuthMiddleware(BaseMiddleware):
	def __init__(self, dp: Dispatcher): #конструктор класса
		super().__init__() #вызываем конструктор родительского класса
		self.dp = dp #ссылка на текущий объект класса
		self.user_repo = UserRepository() #создаем экземплятор репозитория
		


	async def on_pre_process_message(self , message: types.Message, data: Dict[str, Any]) -> None:
		user_id = message.from_user.id
		state = FSMContext(storage=self.dp.storage, chat=message.chat.id, user=user_id) #вручную создаем FSM
		current_state = await state.get_state() if state else None #получаем текущие 

		auth = await self.user_repo.is_authenticated(user_id)

		
		if auth and message.text == "/start":
			await message.answer("Вы уже вошли в аккаунт✔️",reply_markup=user_keyboard())
			raise CancelHandler() #перестает обрабатывать текущие сообщение


		#разрещаем незареганным вводить команды для регестрации
		if not auth and message.text in ["/start" , "/register", "/cancel" , "/help"]:
			return



		#разрещаем пользователю вводыть что угодно пока он регается
		if current_state in AuthOrRegister.states_names:
			return


		if not auth:
			await message.answer("Для начала работы зайдите или зарегистрируйтесь с помощью команды /start")
			raise CancelHandler()



