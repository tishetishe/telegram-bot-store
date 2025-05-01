from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot import dp , bot
from adapters.logs.logger import log_action
from adapters.telegram.keyboard.kb_user import user_kassa
from adapters.telegram.fsm.all_state import Balance
from datetime import datetime
from adapters.database.repositories.user_repository import UserRepository
import re




user_repo = UserRepository()


# Словарь для хранения данных по дням
data_store = {}



# Функция для извлечения чисел
def extract_numbers(text):
    numbers = []
    # Преобразуем все точки в разделители тысяч, если число подходит
    text = text.replace('.', '')
    matches = re.findall(r'-?\d+(?:[кКмМ]?)', text)  # Убираем точку и символы 'к' и 'м'
    
    for match in matches:
        if match.lower().endswith('к'):  # Если число с "к"
            numbers.append(float(match[:-1]) * 1000)
        elif match.lower().endswith('м'):  # Если число с "м"
            numbers.append(float(match[:-1]) * 1000000)  # Преобразуем 'м' в миллион
        else:
            numbers.append(float(match))  # Преобразуем во флоат
    return numbers

# Форматирование числа без копеек и с разделением тысяч
def format_number(num):
    return f"{int(num):,}".replace(",", ".")



# Форматирование числа без копеек и с разделением тысяч
def format_number(num):
    return f"{int(num):,}".replace(",", ".")

# Команда start
@dp.message_handler(commands=['kassa'])
async def send_welcome(message: types.Message) -> None:
    if not await user_repo.is_premium(message.from_user.id):
        await message.answer("Эта функция доступна только с премиумом!\nДля оформления введите /donate")
        return
    await message.reply("Пожалуйста, выберите действие для начала работы", reply_markup=user_kassa())

# Запрашиваем начальную кассу в начале дня
@dp.message_handler(state=Balance.waiting_for_initial_cash)
async def set_initial_cash(message: types.Message, state: FSMContext):
    try:
        initial_cash = float(message.text.replace(' ', '').replace(',', '.'))  # Преобразуем текст в число
        current_date = datetime.now().strftime("%d.%m.%y")

        # Сохраняем начальную кассу в data_store
        if current_date not in data_store:
            data_store[current_date] = {
                "initial_cash": initial_cash,  # Сохраняем начальную кассу
                "income": [],
                "expenses": []
            }

        await state.finish()
        await message.reply(f"Начальная касса на сегодня - {format_number(initial_cash)} руб. Теперь можете начать добавлять доходы и расходы.", reply_markup=user_kassa())

    except ValueError:
        await message.reply("Пожалуйста, введите корректную сумму для начальной кассы.")

# Обработка кнопок "Доход" и "Расход"
@dp.callback_query_handler(lambda c: c.data in ['income', 'expense'])
async def choose(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()  # Отвечаем на callback
    mode = callback_query.data  # Определяем режим
    await state.update_data(mode=mode)  # Сохраняем в памяти
    action = "Доход" if mode == "income" else "Расход"  # Определяем текст для ответа
    await Balance.waiting_for_numbers.set()  # Переход в следующее состояние для чисел
    await callback_query.message.edit_text(f"Отправьте сумму для {action}:")

# Обработка ввода чисел
@dp.message_handler(state=Balance.waiting_for_numbers)
async def process_numbers(message: types.Message, state: FSMContext):
    global data_store

    # Получаем текущий режим (доход или расход)
    data = await state.get_data()
    mode = data.get("mode")

# Извлекаем числа
    numbers = extract_numbers(message.text)
    if not numbers:
        await message.reply("Числа не найдены. Попробуйте снова.")
        return

    # Получаем текущую дату
    current_date = datetime.now().strftime("%d.%m.%y")

    # Если данных на эту дату нет, создаем структуру
    if current_date not in data_store:
        data_store[current_date] = {
            "income": [],
            "expenses": []
        }

    # Добавляем числа в соответствующую категорию
    if mode == "income":
        data_store[current_date]["income"].extend(numbers)
        response = f"Добавлено в доходы: +{format_number(sum(numbers))} руб."
    else:  # Для расхода
        data_store[current_date]["expenses"].extend(numbers)
        response = f"Добавлено в доходы: -{format_number(sum(numbers))} руб."

    # Подсчитываем текущую кассу
    total_income = sum(data_store[current_date]["income"])
    total_expenses = sum(data_store[current_date]["expenses"])
    initial_cash = data_store[current_date].get("initial_cash", 0)  # Получаем начальную кассу (если она задана)
    total_balance = initial_cash + total_income - total_expenses

    await message.reply(response + f"\nТекущая касса: {format_number(total_balance)} руб.", reply_markup=user_kassa())
    await state.finish()

# Завершение дня
@dp.callback_query_handler(lambda c: c.data == "end")
async def end_day(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_date = datetime.now().strftime("%d.%m.%y")

    if current_date not in data_store:
        await callback_query.message.edit_text("Нет данных для этого дня.")
        return

    # Получаем информацию по доходам и расходам
    income = data_store[current_date]["income"]
    expenses = data_store[current_date]["expenses"]
    initial_cash = data_store[current_date].get("initial_cash", 0)

    # Формируем отчет по расходам
    expenses_report = "\n".join([f"Отдал - {format_number(e)} " for e in expenses])
    income_report = "\n".join([f"Снял - {format_number(i)} " for i in income])

    # Итог
    total_income = sum(income)
    total_expenses = sum(expenses)
    total_balance = initial_cash + total_income - total_expenses

    # Формируем итоговый отчет
    await callback_query.message.edit_text(
        f"{current_date}\n"
        f"☀️Касса в начале дня - {format_number(initial_cash)} \n"
        f"Доходы:\n{income_report}\n\n"
        f"👉Итог:\n{expenses_report}\n\n"
        f"\n"
        f"🏦Снял - {format_number(total_income)}\n"
        f"📎Принял товар - {format_number(total_expenses)} \n"
        f"🏁Касса в конце дня - {format_number(total_balance)} ",
        reply_markup=user_kassa()
    )

    # Очищаем данные после завершения дня
    data_store.clear()