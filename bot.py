#тут будет инициализация бота
from aiogram import types
from aiogram import Bot , Dispatcher
import config
from adapters.logs.logger import log_error
from aiogram.contrib.fsm_storage.redis import RedisStorage2




bot = Bot(token=config.TOKEN) #передаем токен
storage = RedisStorage2(host='redis' , port=6379 , db=5)
dp = Dispatcher(bot,storage=storage)




@dp.errors_handler()#хендллер работающий с ошибками
async def error_handler(update, exception):
	await log_error(exception) #Записывакм ошибку в логи
	return True #что бы бот не упал крч