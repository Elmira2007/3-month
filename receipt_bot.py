from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from logging import basicConfig, INFO
from config import token 
from fpdf import FPDF
import time, os, requests, sqlite3, uuid

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
basicConfig(level=INFO)

connection = sqlite3.connect('client.db')
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INT,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created VARCHAR(100)
);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS receipt(
    payment_code INT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    direction VARCHAR(100),
    month VARCHAR(100),
    amount INT,
    date VARCHAR(100)
);
""")

start_buttons = [
    types.InlineKeyboardButton('Оплатить и получить чек', callback_data='payment_receipt'),
    types.InlineKeyboardButton('Тестовая кнопка', callback_data='testing_button'),
    types.InlineKeyboardButton('Наш сайт', url='https://geeks.kg')
]
start_keyboard = types.InlineKeyboardMarkup().add(*start_buttons)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    cursor.execute(f"SELECT id FROM users WHERE id = {message.from_user.id};")
    exists_user = cursor.fetchall()
    if not exists_user:
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?);', 
                       (message.from_user.id, message.from_user.username,
                        message.from_user.first_name, message.from_user.last_name,
                        time.ctime()))
        cursor.connection.commit()
    await message.answer(f"Привет {message.from_user.full_name}", reply_markup=start_keyboard)

@dp.callback_query_handler(lambda call: call.data == "testing_button")
async def testing_function(callback:types.CallbackQuery):
    await callback.message.answer("Тестовая кнопка сработала! :) ")

class ReceiptState(StatesGroup):
    first_name = State()
    last_name = State()
    direction = State()
    month = State()
    amount = State()

@dp.callback_query_handler(lambda call: call.data == 'payment_receipt')
async def start_receipt(message:types.CallbackQuery):
    await message.message.answer("Ввведите следующие данные для получения онлайн чека:")
    await message.message.answer("Введите свое имя:")
    await ReceiptState.first_name.set()

@dp.message_handler(state=ReceiptState.first_name)
async def get_last_name(message:types.Message, state:FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Отлично, теперь вашу фамилию:")
    await ReceiptState.last_name.set()

@dp.message_handler(state=ReceiptState.last_name)
async def get_direction(message:types.Message, state:FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Прекрасно, введите свое направление:")
    await ReceiptState.direction.set()

@dp.message_handler(state=ReceiptState.direction)
async def get_month(message:types.Message, state:FSMContext):
    await state.update_data(direction=message.text)
    await message.answer("Теперь месяц, за которую вы оплатили курс:")
    await ReceiptState.month.set()

@dp.message_handler(state=ReceiptState.month)
async def get_amount(message:types.Message, state:FSMContext):
    await state.update_data(month=message.text)
    await message.answer("Сколько сом вы оплатили?")
    await ReceiptState.amount.set()

@dp.message_handler(state=ReceiptState.amount)
async def generate_receipt(message:types.Message, state:FSMContext):
    await state.update_data(amount=message.text)
    result = await storage.get_data(user=message.from_user.id)
    generate_payment_code = int(str(uuid.uuid4().int)[:10])
    print(result)
    print(generate_payment_code)
    cursor.execute("INSERT INTO receipt VALUES (?, ?, ?, ?, ?, ?, ?);",
                   (generate_payment_code, result['first_name'],
                    result['last_name'], result['direction'],
                    result['month'], result['amount'],
                    time.ctime() ))
    cursor.connection.commit()
    receipt_text = f"""Оплата курса {result['direction']}
Имя: {result['first_name']}
Фамилия: {result['last_name']}
Направление: {result['direction']}
Месяц: {result['month']}
Количество: {result['amount']}
Код оплаты: {generate_payment_code}
Время: {time.ctime()}"""
    await message.answer(receipt_text)
    await bot.send_message(-4066726453, receipt_text)
    #Работа с PDF файлом
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Arial', size=12)
    pdf.cell(100, 10, txt=f"Payment courses {result['direction']}", ln=True)
    pdf.cell(100, 11, txt=f"First Name: {result['first_name']}", ln=True)
    pdf.cell(100, 12, txt=f"Last Name: {result['last_name']}", ln=True)
    pdf.cell(100, 13, txt=f"Direction: {result['direction']}", ln=True)
    pdf.cell(100, 14, txt=f"Month: {result['month']}", ln=True)
    pdf.cell(100, 15, txt=f"Amount: {result['amount']}", ln=True)
    pdf.cell(100, 16, txt=f"Payment Code: {generate_payment_code}", ln=True)
    pdf.cell(100, 17, txt=f"Time: {time.ctime()}", ln=True)

    if not os.path.exists('receipt'):
        os.mkdir('receipt')

    pdf.output(f'receipt/{generate_payment_code}.pdf')
    with open(f'receipt/{generate_payment_code}.pdf', 'rb') as receipt_pdf_file:
        await message.answer_document(receipt_pdf_file)
    with open(f'receipt/{generate_payment_code}.pdf', 'rb') as receipt_pdf_file:
        await bot.send_document(-4066726453, receipt_pdf_file)
    os.remove(f'receipt/{generate_payment_code}.pdf')
    await state.finish()

executor.start_polling(dp, skip_updates=True)