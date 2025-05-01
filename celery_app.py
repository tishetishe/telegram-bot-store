from celery import Celery 
import os
from dotenv import load_dotenv
from aiogram import Bot
import asyncio


load_dotenv() #загружаем переменные из .env

#указываем где искать брокер сообщений
CELERY_BROKER_URL = "redis://redis:6379/0" 


BOT_TOKEN = os.getenv("TOKEN")

app = Celery('worker' , broker=CELERY_BROKER_URL) #запускаем

bot = Bot(token=BOT_TOKEN) #присваимаем токен

@app.task
def log_action(user_id : int , action: str):
	with open("bot_logs.txt" , "a" , encoding="utf-8") as f:
		f.write(f"User {user_id}: {action}\n")


@app.task
def send_mass_message(user_ids: list , text: str):
	loop = asyncio.new_event_loop() #создаем луп тк это не асинхронка
	asyncio.set_event_loop(loop)
	loop.run_until_complete(_send_all(user_ids , text))

async def _send_all(user_ids , text):
	async with Bot(token=BOT_TOKEN) as bot:
		for user_id in user_ids:
			try:
				await bot.send_message(chat_id=user_id , text=text)
			except Exception as e:
				print(f"Ошибка при отправке {user_id}: {e}")