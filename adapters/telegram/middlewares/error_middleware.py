from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.dispatcher.handler import CancelHandler
from adapters.logs.logger import log_error
from config import ADMINS



class ErrorMiddleware(BaseMiddleware):
	async def on_post_process_message(self, message: types.Message , results , data):
		try:
			if isinstance(results, Exception):
				raise results #функция(isinstance) проверяет является ли result объектом ошибки,а raise выбрасывает ошибку
		except Exception as e:
			await log_error(f"Ошибка в сообщении от {message.from_user.id}: {str(e)}")

			for admin_id in ADMINS:
				try:
					await message.bot.send_message(admin_id , f"Ошибка у пользователя {message.from_user.id}:\n<code>{str(e)}</code>", parse_mode="HTML")
				except Exception:
					pass

			await message.answer("Произошла ошибка, мы уже работаем над этим.") #ответ юзеру
			raise CancelHandler() #прерывет дальнейщую обработку сообщений


		
