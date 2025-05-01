import aiosqlite
from config import DB_NAME_DEFECT



class DefectRepocitory:
	def __init__(self ,db_name=DB_NAME_DEFECT):
		self.db_name=db_name





	async def register_defect(self,user_id, data_brack, name_phone, city, imei, is_defect, photo_defect):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute("INSERT INTO bracki(user_id, data_brack, name_phone, city, imei, is_defect, photo_defect) VALUES(?,?,?,?,?,?,?)",
			(user_id, data_brack, name_phone, city, imei, is_defect, photo_defect))

			await db.commit()




	async def succes_defect(self , user_id, data_bs, phone_bs, city_bs, imei_bs, CDEK):
		async with aiosqlite.connect(self.db_name) as db:
			await db.execute("INSERT INTO success_braki(user_id, data_bs, phone_bs, city_bs, imei_bs, CDEK) VALUES(?,?,?,?,?,?)",
			(user_id, data_bs, phone_bs, city_bs, imei_bs, CDEK))

			await db.commit()




	async def get_all_braki(self , user_id):
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT data_brack, name_phone, city, imei, is_defect, photo_defect FROM bracki WHERE user_id = ?",(user_id,)) as cursor:
				return await cursor.fetchall()



	async def get_success_braki(self ,user_id):
		async with aiosqlite.connect(self.db_name) as db:
			async with db.execute("SELECT data_bs, phone_bs, city_bs, imei_bs, CDEK FROM success_braki WHERE user_id = ?",(user_id,)) as cursor:
				return await cursor.fetchall()


