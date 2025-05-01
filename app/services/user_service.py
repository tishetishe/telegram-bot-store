import time 
from adapters.database.repositories.user_repository import UserRepository
from adapters.logs.logger import log_error , log_warning , log_action

class UserService:
	def __init__(self, user_repo: UserRepository):
		self.user_repo = user_repo
		 


	async def is_spam(self, user_id: int, cooldown: int = 3) -> bool:
		try:
			row = await self.user_repo.get_last_command_time(user_id)
			current_time = time.time()#текущие время(типо 1.1)

			if row and row[0] is not None:
				try:
					last_time = float(row[0]) #время послдней команды(указываем на то , что это обязательно float)
				except (ValueError, TypeError):
					await log_warning(user_id , f"Некоректное значение времени - {row[0]}")
					last_time = 0  #если ошибка связана с заменой на текст или на другой тип числа


			else:
				last_time = 0 #в любой непонятной хуйне ставим 0

			if current_time - last_time < cooldown: #если кд больше,чем прошло времени с отправки, то блокаем сообщение
				await log_action(user_id , "FLOOD DETECTED ") #логгируем трабл
				return True #если прошло меньше времени, чем кд

			await self.user_repo.update_command_time(user_id, current_time)
			return False

		except Exception as e:
			return False #не блокируем если что-то пошло не так