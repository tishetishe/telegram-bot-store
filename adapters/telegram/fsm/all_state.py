from aiogram.dispatcher.filters.state import State, StatesGroup


class AuthOrRegister(StatesGroup):
	register_password_user = State()
	register_login_user = State()
	auth_login = State()
	auth_password = State()


class Brack(StatesGroup):
	data_brack = State()
	name_phone = State()
	city = State()
	imei = State()
	is_defect = State()
	photo_defect = State() 



class SBrack(StatesGroup):
	data_bs = State()
	phone_bs = State()
	city_bs = State()
	imei_bs = State()
	CDEK = State()



class Mail(StatesGroup):
	watch_text = State()



class OrderProcess(StatesGroup):
	search = State()
	confirm = State()
	phone = State()
	fio = State()
	city_address = State()



class Balance(StatesGroup):
    waiting_for_initial_cash = State()  
    waiting_for_income_or_expense = State()  
    waiting_for_numbers = State()  