import logging
import asyncio


logging.basicConfig(
  filename="bot_logs.txt", #имя файла куда будут записываться логи
  level=logging.INFO, #уровень логов в важности
  format="%(asctime)s - %(levelname)s - %(message)s", #формат сообщения
  encoding="utf-8" #хуярим на русский
)


logger = logging.getLogger(__name__) #название нашего логера

async def log_action(user_id, action):
  await asyncio.to_thread(logging.info, f"User {user_id}: {action}")#информируем о действиях пользователей


async def log_error(error):
  await asyncio.to_thread (logging.error, f"{error}", exc_info=True) #добовляет полное описание ошибок(стек вызовов)'



async def log_warning(warning):
  await asyncio.to_thread(logging.warning, warning)