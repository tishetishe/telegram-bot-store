from aiogram import types
from config import ADMINS
from functools import wraps


#Декоратор на проверку админки


#создаем функцию которая будет проветь админ ли пользователь или нет
def is_admin(func): #func - любая переданная функция
    @wraps(func)
    async def wrapper(message: types.Message , *args, **kwargs):
    	if message.from_user.id not in ADMINS:
    		await message.answer("Вы не имейте доступ к этой команде")
    		return
    	return await func(message , *args, **kwargs)

    return wrapper
