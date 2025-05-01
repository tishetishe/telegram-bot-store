import aiosqlite
import datetime
import aiofiles
import hashlib
import time
from config import DB_NAME_USERS


class UserRepository:
	def __init__(self, db_name=DB_NAME_USERS):
		self.db_name=db_name


	async def is_login_take(self, login: str) -> bool:
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT 1 FROM users WHERE login = ?", (login,)) as cursor:
				return await cursor.fetchone() is not None #вернет если есть такой логин(сравниваем)



	async def user_exists(self, user_id: int) -> bool:
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT login, password FROM users WHERE user_id = ?", (user_id,)) as cursor:
				user = await cursor.fetchone()
				return user is not None and all(user) #проверяет есть ли пользователь в бд



	async def set_maintenance(self, status: int):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute("UPDATE users SET maintenance = ?", (status,))
			await db.commit() #обновляем и заменяем на status который у нас в другом коде



	async def is_maintenance(self) -> bool:
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT maintenance FROM users") as cursor:
				row = await cursor.fetchone() #результат запроса из бд
				return row and row[0] == 1 #проверяет находиться ли бот в тех-работах




	async def get_last_command_time(self, user_id: int):
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT last_command_time FROM users WHERE user_id = ?",(user_id,)) as cursor:
				row = await cursor.fetchone() #выбираем значение из таблицы где послдние время команды
				return row




	async def update_command_time(self, user_id: int , timestamp: float):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute(
				"INSERT INTO users (user_id, last_command_time) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET last_command_time = excluded.last_command_time",
				(user_id, timestamp)#обновляет время на текущие
			)
			await db.commit()



	async def get_all_users(self) -> bool:
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT user_id FROM users") as cursor:
				users = await cursor.fetchall()#получаем всю таблицу(в виде кортежа) с юзером айди
				return [user[0] for user in users] #получаем иминно сами цифры(user_id), а не кортеж




	async def set_authenticated(self, user_id: int, status: bool):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute("UPDATE users SET is_auth = ? WHERE user_id = ?",(1 if status else 0, user_id))
			#записывает статус входа в бд(1 - вошел, 0 - вышел)
			await db.commit()




	async def is_authenticated(self, user_id: int) -> bool:
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT is_auth FROM users WHERE user_id = ?",(user_id,)) as cursor:
				row = await cursor.fetchone()
				return row[0] == 1 if row else False #проверяем вошел ли пользователь, иначе возвращаем, что он вышел



	async def is_premium(self , user_id: int) -> bool:
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT premka FROM users WHERE user_id = ?", (user_id,)) as cursor:
				row = await cursor.fetchone()
				return row[0] == 1 if row else False



	async def set_premium(self, user_id: int, status: bool):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute("UPDATE users SET premka = ? WHERE user_id = ?",(1 if status else 0 , user_id))
			await db.commit()




	async def register_login(self, user_id: int , login: str):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute(
			"INSERT INTO users (user_id,login) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET login = excluded.login",(user_id,login)
			)
			await db.commit()#если уже айдишник есть,то обновляем только данные




	async def register_password(self, user_id: int, password: str):
	#hashed_password = bcrypt.hashpw(password.encode(), bcrypt.getsalt())
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute("UPDATE users SET password = ? WHERE user_id = ?",(password, user_id))
			await db.commit()#юзер уже есть в бд,нам просто следует "обновить" пароль




	async def login(self, user_id: int):
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT login , password FROM users WHERE user_id = ?", (user_id,)) as cursor:
				return await cursor.fetchone()


	async def get_user_debt(self,user_id):
		async with aiosqlite.connect(self.db_name) as db:
			cursor = await db.execute("SELECT debt FROM users WHERE user_id = ?",(user_id,))
			row = await cursor.fetchone()
			return row[0] if row else 0



	async def update_user_debt(self, user_id , amount):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute("INSERT INTO users (user_id , debt) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET debt = debt + ?",(user_id, amount , amount))
			await db.commit()


