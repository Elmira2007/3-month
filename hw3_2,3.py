from aiogram import Bot, Dispatcher, types, executor
from config import token
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from logging import basicConfig, INFO
import sqlite3, time


bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
basicConfig(level=INFO)

connect = sqlite3.connect("ojak_kebab_bot.db")
cursor = connect.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(100),
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        date_joined DATETIME
    );
""")
connect.commit()

start_buttons = [
    types.KeyboardButton('Меню'),
    types.KeyboardButton('О нас'),
    types.KeyboardButton('Адрес'),
    types.KeyboardButton('Заказать еду')
]
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*start_buttons)

@dp.message_handler(commands='start')
async def start(message:types.Message):
     cursor = connect.cursor()
     cursor = cursor.execute(f"SELECT * FROM users WHERE id = {message.from_user.id};")
     res = cursor.fetchall()
     print(res)
     if not res: 
        cursor.execute(f"""INSERT INTO users (id, username, first_name, last_name, date_joined) VALUES ({message.from_user.id},
                       '{message.from_user.username}',
                       '{message.from_user.first_name}',
                       '{message.from_user.last_name}',
                       '{time.ctime()}'
                       );""")
        connect.commit()
     await message.answer(f"Приветствую вас, {message.from_user.full_name}!", reply_markup=start_keyboard)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        title VARCHAR(100),
        phone_number VARCHAR(100),
        address VARCHAR(100)
    );
""")
connect.commit()

class OrderFoodState(StatesGroup):
    name = State()
    title = State()
    phone_number = State()
    address = State()

@dp.message_handler(text='Меню')
async def menu(message:types.Message):
    await message.answer("МЕНЮ: отдел шашлыки: https://ocak.uds.app/c/goods?categoryId=498873")

@dp.message_handler(text='О нас')
async def abont_us(message:types.Message):
    await message.reply(" https://ocak.uds.app/c/about")


@dp.message_handler(text='Адрес')
async def send_address(message:types.Message):
    await message.answer("📌 Адрес: \n г. Бишкек, Чуй проспект, 76Б \n  Наши контакты: \n\n +996312979845 \n +996990006122")
    await message.answer_location(42.817709, 74.557861)

@dp.message_handler(text='Заказать еду')
async def order_foor(message:types.Message):
    await message.answer(f"Введите свое имя ")
    await OrderFoodState.name.set()

@dp.message_handler(state=OrderFoodState.name)
async def ordes(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer("Что хотите заказать? ")
    await OrderFoodState.next()

@dp.message_handler(state=OrderFoodState.title)
async def ordes(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await message.answer("Введите свой номер телефона? ")
    await OrderFoodState.next()

import re

@dp.message_handler(state=OrderFoodState.phone_number)
async def process(message: types.Message, state: FSMContext):
    phone_number = message.text

    # Проверка номера телефона с использованием регулярного выражения
    if re.match(r'^\+?\d{1,3}?\d{9,15}$', phone_number):
        async with state.proxy() as data:
            data['phone_number'] = phone_number

        await message.answer("Введите свой адрес")
        await OrderFoodState.next()
    else:
        await message.answer("Некорректный номер телефона. Пожалуйста, введите корректный номер.")


@dp.message_handler(state=OrderFoodState.phone_number)
async def process(message: types.Message, state: FSMContext):
     async with state.proxy() as data:
         data['phone_number'] = message.text

     await message.answer("Введите свой адрес")
     await OrderFoodState.next()


@dp.message_handler(state=OrderFoodState.address)
async def food_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text


    async with state.proxy() as data:
        name = data['name']
        title = data['title']
        phone_number = data['phone_number']
        address = data['address']

    cursor.execute('''
        INSERT INTO orders(name, title, phone_number, address)
        VALUES (?, ?, ?, ?)
    ''', (name, title, phone_number, address))
    connect.commit()

    await message.answer("Ваш заказ принять.\nОн когда нибудь приедит")
    await state.finish()



executor.start_polling(dp, skip_updates=True)