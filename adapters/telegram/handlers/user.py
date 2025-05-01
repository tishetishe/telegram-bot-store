import re
import requests
from aiogram.dispatcher import filters
from aiogram.types import CallbackQuery
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from bot import dp , bot
from adapters.logs.logger import log_action
from config import GROUP_ID , CHANNEL_ID
from adapters.telegram.keyboard.kb_user import user_keyboard , user_item
from adapters.logs.logger import log_action
from adapters.telegram.fsm.all_state import OrderProcess





@dp.message_handler(lambda message: message.text == "📌F.A.Q")
async def faq(message: types.Message):
    await message.answer(
        "*•Каким способом отправляйте устройство?*\n\nМы отправляем через СДЭК, Почтой России, а для более крупных заказов — аэропортом Шереметьево.\n\n"
        "*•Какие способы оплаты у вас есть?*\n\nЧерез данного бота способ оплаты в USDT.\n\n"
        "*•Какие товары вы продаете?*\n\nМы продаем iPhone, iPad, AirPods, MacBook, PlayStation, Dyson и многие другие товары.\n\n"
        "*•Что делать, если у меня брак?*\n\nНапишите нашему менеджеру, предоставьте IMEI с коробки и устройства. В течение 30 дней мы заменим товар или вернем деньги.\n\n"
        "*•Какие данные нужны для отправки?*\n\nФИО, номер телефона и адрес вашего СДЭК или Почты России. Доставку оплачиваете вы.",
        parse_mode="Markdown",reply_markup=user_keyboard()
    )

@dp.message_handler(lambda message: message.text == "💬Отзывы")
async def comment_cmd(message: types.Message):
    await message.answer("Наши отзывы👇\n[Отзывы](https://t.me/chronodevotzov)", reply_markup=user_keyboard(),parse_mode="Markdown")

@dp.message_handler(lambda message: message.text == "📞Поддержка")
async def support_cmd(message: types.Message):
    await message.answer("Нет интересующего устройства или есть вопросы?\nПишите нам! - @chrona_seller",reply_markup=user_keyboard())

@dp.message_handler(lambda message: message.text == "💰Наш прайс")
async def price_cmd(message: types.Message):
    await message.answer("Наш прайс👇\n[Прайс](https://t.me/chronodevice)", reply_markup=user_keyboard(),parse_mode="Markdown")


@dp.message_handler(lambda message: message.text == "🛒Покупка товаров из прайса")
async def buy_iphone_cmd(message: types.Message):
    await message.answer("Введите название устройства с флагом страны в начале как в прайсе без цены\n(например: 🇮🇳 13 512 Blue)", reply_markup=user_keyboard())
    await OrderProcess.search.set()



@dp.message_handler(state=OrderProcess.search)
async def search_cmd(message: types.Message, state: FSMContext):
	query = message.text.strip().lower() #сообщение юзера
	chat = await bot.get_chat(CHANNEL_ID) #получаем тгк канал

	if not chat.pinned_message:
		await message.answer("В канале нет закрепленного сообщения")
		return

	pinned_text = chat.pinned_message.text.lower() #получаем закрепленное сообщение и переводим в нижний регистер
	pattern = rf"{re.escape(query)}\s*[-–—]\s*(\d+)" #ищем в закрепе совпадения по этому шаблону
	match = re.search(pattern , pinned_text) #ищем совпадение в тексте пользователя и тгк

	if not match:
		await message.answer("Товар был не найден")
		return

	price = int(match.group(1)) #из pattern извлекаем цену "(\d+)"
	await state.update_data(product=query, price=price) #сохраяем в Fsm

	await message.answer(f"Товар: {query}\nЦена: {price}" , reply_markup=user_item())
	await OrderProcess.confirm.set()




@dp.callback_query_handler(lambda c: c.data in ["save_teh" , "cancel_teh"] , state=OrderProcess.confirm) #получаем список callback_data и СТАВИМ СОСТОЯНИЕ БЛЧТЬ
async def confirm_product(call: types.CallbackQuery , state: FSMContext):
	if call.data == "cancel_teh":
		await call.message.edit_text("Действие отменино")
		await state.finish()
	else:
		await call.message.answer("Введите ваш номер телефона")
		await OrderProcess.phone.set()
	await call.answer() #завершаем наш callback(?)




@dp.message_handler(state=OrderProcess.phone)
async def get_phone(message: types.Message , state: FSMContext):
	await state.update_data(phone=message.text.strip())
	await message.answer("Введите ваше ФИО и ваш юзернейм в скорбках\n Например -> Иван Иванов (@forexemple)")
	await OrderProcess.fio.set()



@dp.message_handler(state=OrderProcess.fio)
async def get_fio(message: types.Message , state: FSMContext):
	await state.update_data(fio=message.text.strip())
	await message.answer("Введите ваш город и пункт выдачи\n(Пример: Москва , Манежная площадь 1 стр. 2)")
	await OrderProcess.city_address.set()



@dp.message_handler(state=OrderProcess.city_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(city_address=message.text.strip())
    data = await state.get_data()
    username = message.from_user.full_name or message.from_user.username or "Неизвестно" #добавляем имя пользователя/никнейм

    #ОБЯЗАТЕЛЬНО указываем напрямую , ибо product и price к примеру вообще в другом куске кода , где data не может определить просто так

    product = data.get("product", "-")
    price = data.get("price", "-")
    phone = data.get("phone", "-")
    fio = data.get("fio", "-")
    city_address = data.get("city_address" , "-")



    await log_action(message.from_user.id, f"Оформил заказ: {product} за {price}, номер: {phone} , ФИО: {fio} , адрес: {city_address}")

    final_message = (
        f"🎉 Новый заказ!\n\n"
        f"📦 Товар: {product}\n"
        f"💰 Сумма: {price}\n\n"
        f"📞 Телефон: {phone}\n"
        f"📋 ФИО: {fio}\n"
        f"📍 Адрес доставки: {city_address}\n"
        f"👤 Пользователь: {username}"
    )



    
    await bot.send_message(chat_id=GROUP_ID, text=final_message, parse_mode="Markdown") #Отправляем сообщение в группу
    await message.answer("Спасибо! Ваш заказ был отправлен.\nМы свяжемся с вами для подтверждения.\n\nЕсли вы неверно написали данные,то напишите в поддержку❗️")
    await state.finish()

     


@dp.message_handler(Command('cancel'), state="*")
async def cancel_cmd_user(message: types.Message , state: FSMContext):
	currant_state = await state.get_state() #получем текущие состояние 
	print(f"Текущие состояние: {currant_state}")
	if currant_state is None:
		await message.answer("У вас нет активного действия")
		return 

	await state.finish()
	await message.reply("Действие отменино" , reply_markup=user_keyboard())