from aiogram import Bot, Dispatcher, types, executor
from config import token
from bs4 import BeautifulSoup
from aiogram.types import ParseMode
import requests
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

connect = sqlite3.connect('ultra.db')
cursor = connect.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        price INTEGER PRIMARY KEY,
        availability VARCHAR(200),
        laptop_info TEXT
    );
''')
connect.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS goods(
        id INTEGER PRIMARY KEY,
        title TEXT,
        price INTEGER
);
""")
connect.commit()

class OrderFoodState(StatesGroup):
    title = State()
    price = State()

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer("Здравствуйте, вас приветствует магазин ноутбуков ULTRA.KG")
   
@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await message.reply("Доступные команды:\n"
                        "/start - начать чат\n"
                        "/info - Информация о магазине ноутбуков https://www.sulpak.kg/f/noutbuki\n"
                        "/laptops - Отправляет ноутбуки в наличии\n"
                        "/help - вывести список доступных команд\n"
                        "/buy - Купить ноутбук \n"
                        "/bucket - посмотреть карзину")
                        

@dp.message_handler(commands='laptops')
async def send_laptops(message:types.Message):
    await message.answer("Отправляю ноутбуки в наличии....")

    n = 0
    for page in range(1,7):
            url = f'https://www.sulpak.kg/f/noutbuki?page={page}'
            response = requests.get(url=url)
            print(response) 
            soup = BeautifulSoup(response.text, 'lxml')
            all_laptops = soup.find_all('div', class_='product__item-name')
            all_prices = soup.find_all('div', class_='product__item-price')


            for laptop, price in zip(all_laptops, all_prices):
                n+=1
                # print(n,laptop.text,"".join(price.text.split()))
                price_laptop = " ".join(price.text.split())
                await message.answer(f"{n} {laptop.text} {price_laptop}")
    await message.answer("Вот все ноутбуки в наличии")

@dp.message_handler(commands='bucket')
async def bucket(message: types.Message):

    # user = message.text
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM goods WHERE id ")
    title1 = cursor.fetchall()
    print(title1)
    await message.answer(f"ваша карзина: {title1}\n\n")
    cursor.close()
    connect.close()
#fetchall() – возвращает число записей в виде упорядоченного списка; fetchmany(size) – возвращает число записей не более size; fetchone() – возвращает первую запись.

@dp.message_handler(commands='buy')
async def order_foor(message:types.Message):
    await message.answer(f"Введите название товара ")
    await OrderFoodState.title.set()
    
@dp.message_handler(state=OrderFoodState.title)
async def ordes(message:types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await message.answer("цена товара: ")
    await OrderFoodState.next()

@dp.message_handler(state=OrderFoodState.price)
async def food_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
        
    async with state.proxy() as data:
        title = data['title']
        price = data['price']
        
    cursor.execute('''
        INSERT INTO goods (title, price)
        VALUES (?, ?)''', (title, price))
    connect.commit()

    await message.answer("Ваш ноутбук добавлен в корзину")
    await state.finish()

executor.start_polling(dp, skip_updates=True)
