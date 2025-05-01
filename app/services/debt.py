from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp , bot
from adapters.logs.logger import log_action
from adapters.telegram.keyboard.kb_user import user_debt
from adapters.database.repositories.user_repository import UserRepository



user_repo = UserRepository()


@dp.message_handler(commands=['debt'])
async def debt_cmd(message: types.message):
	if not await user_repo.is_premium(message.from_user.id):
		await message.answer("Эта функция доступна только с премиумом!\nДля оформления введите /donate")
		return
	user_id = message.from_user.id
	debt = await user_repo.get_user_debt(user_id) #из репозитория извлекаем наш текущий долг
	await message.answer(f"Ваш текущий долг: {debt}", reply_markup=user_debt())
	



@dp.callback_query_handler(lambda c: c.data in ["plus_debt" , "minus_debt"])
async def confirm_product(callback: types.CallbackQuery , state: FSMContext):
	action = callback.data #действие пользователя
	await state.update_data(debt_action=action) #сохраняем выбранное действие
	await callback.message.answer("Введите сумму:")
	await state.set_state("debt_input") #переводим в другое состояние
	await callback.answer()



@dp.message_handler(state="debt_input")
async def debt_input_cmd(message: types.message , state: FSMContext):
	user_id = message.from_user.id
	user_data = await state.get_data()
	action = user_data.get("debt_action") #достаем сохранненое действие

	try:
		amount = int(message.text) #указываем что тест именно число

	except ValueError:
		await message.answer("Введите число")
		return

	if action == "plus_debt":
		await user_repo.update_user_debt(user_id, +amount) #прибавляем через бд
		await message.answer(f"Добавлено {amount} в долг")

	else:
		await user_repo.update_user_debt(user_id, -amount)
		await message.answer(f"Уменьшино {amount} из долга") #уменьшаем через бд

	await state.finish()


		