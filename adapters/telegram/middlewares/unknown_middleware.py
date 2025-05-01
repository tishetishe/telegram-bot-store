from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import Message


class UnknownMiddleware(BaseMiddleware):
	async def on_pre_process_message(self , message: types.Message , data: dict):
		state: FSMContext = data.get("state") #получаем FSM
		current_state = await state.get_state() if state else None #текущие состояние

		


		if message.text and message.text.startswith('/'):
			known_commands = {
			'/start' , '/logout' , '/adminka' , '/help' , '/cancel' , '/test_prem' ,  '/set_success_brak' ,
			'/set_brack' , '/donate' , '/braki' , '/succes_braki' , '/debt' , '/kassa'

			}
			
			
			if message.text.split()[0] not in known_commands:
				await message.answer("У меня нет такой команды, воспользуйтесь /help , что бы узнать весь список команд")
				raise CancelHandler()
				#split -> берет первое слово команды
				