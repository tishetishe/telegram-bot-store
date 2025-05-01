#главный файл запуска бота
from aiogram import executor
from bot import dp #импортируем наш диспетчер
import adapters.telegram.handlers.start #команда старт
import adapters.telegram.handlers.admin
import adapters.telegram.handlers.braks
import adapters.telegram.handlers.success_braks
import adapters.telegram.handlers.other
import adapters.telegram.handlers.user
from adapters.database.db import db_setup
from adapters.database.defect_db import defect_table
from app.services.user_service import UserService
import app.services.debt
import app.services.kassa 
from adapters.database.repositories.user_repository import UserRepository
import tracemalloc
from adapters.telegram.middlewares.error_middleware import ErrorMiddleware
from adapters.telegram.middlewares.auth_middleware import AuthMiddleware
from adapters.telegram.middlewares.anti_flood_middleware import AntiFloodMiddleware
from adapters.telegram.middlewares.unknown_middleware import UnknownMiddleware




tracemalloc.start()

user_repo = UserRepository()
user_service = UserService(user_repo)


dp.middleware.setup(ErrorMiddleware())
dp.middleware.setup(AuthMiddleware(dp))
dp.middleware.setup(AntiFloodMiddleware(user_service , user_repo))#подключаем миддлвери к коду
dp.middleware.setup(UnknownMiddleware())



async def on_startup(_):
	await db_setup()
	await defect_table() #соеденяем нашу таблицу с ботом
	print("Бот работает!")


executor.start_polling(dp , on_startup=on_startup, skip_updates=True)