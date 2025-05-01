from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types
from aiogram.types import Message
from typing import Dict, Any
from adapters.database.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from aiogram.dispatcher.handler import CancelHandler
from config import ADMINS

class AntiFloodMiddleware(BaseMiddleware):
	def __init__(self, user_service: UserService , user_repo: UserRepository):
		super().__init__() #вызываем конструктор родителя
		self.user_service = user_service
		self.user_repo = user_repo
		self.warned_users = set() #список игнора
		



	async def on_pre_process_message(self, message: types.Message, data: Dict[str, Any]):
		user_id = message.from_user.id

		if await self.user_service.is_spam(user_id): #проверяем пользователя на спам
			if user_id not in self.warned_users:
				self.warned_users.add(user_id) #добавляем в список игнора , если спаммит люто
				await message.answer("Не флудите пожалуйста(")
			raise CancelHandler() #отменяем обработку

		if user_id in self.warned_users:
			self.warned_users.remove(user_id) #удаляем с игнора , если перестал спамить




		if message.from_user.id not in ADMINS:
			if await self.user_repo.is_maintenance():
				await message.answer("🚧В данный момет введуться тех-работы🚧")
				raise CancelHandler()