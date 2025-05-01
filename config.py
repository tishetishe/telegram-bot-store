import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="token.env")

TOKEN = os.getenv("TOKEN") #типо подключаемся из файла .env

DB_NAME_USERS = os.getenv("DB_NAME_USERS")
DB_NAME_DEFECT = os.getenv("DB_NAME_DEFECT")

LOG_FILE = os.getenv("LOG_FILE")

GROUP_ID = int(os.getenv("GROUP_ID"))

CHANNEL_ID = os.getenv("CHANNEL_ID")

ADMINS = list(map(int, os.getenv("ADMINS").split(","))) #делаем список админов