#база данных
import aiosqlite
import datetime
import aiofiles
import hashlib
import time
from config import DB_NAME_USERS , LOG_FILE 
import bcrypt




async def db_setup():
	async with aiosqlite.connect(DB_NAME_USERS) as db:
		await db.execute("""
		CREATE TABLE IF NOT EXISTS users (
			user_id INTEGER PRIMARY KEY,
			login TEXT,
			password TEXT,
			last_command_time REAL,
			is_auth INTEGER DEFAULT 0,
			maintenance INTEGER DEFAULT 0,
			premka INTEGER DEFAULT 0,
			debt INTEGER DEFAULT 0
		)
		""")

		await db.commit()





