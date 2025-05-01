import aiosqlite
import datetime
import aiofiles
import hashlib
import time
from config import DB_NAME_DEFECT , LOG_FILE 
import bcrypt



async def defect_table():
	async with aiosqlite.connect(DB_NAME_DEFECT) as db:
		await db.execute("""
		CREATE TABLE IF NOT EXISTS bracki (
		user_id TEXT,
		data_brack TEXT,
		name_phone TEXT,
		city TEXT,
		imei TEXT,
		is_defect TEXT,
		photo_defect Text

		)
		""")


		await db.execute("""
		CREATE TABLE IF NOT EXISTS success_braki(
		user_id TEXT,
		data_bs TEXT,
		phone_bs TEXT,
		city_bs TEXT,
		imei_bs TEXT,
		CDEK INTEGER
		)
		""")

		await db.commit()
