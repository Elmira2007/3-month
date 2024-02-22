import logging
import sqlite3
from aiogram import Bot, Dispatcher, types,executor
from aiogram import executor
from config import token
logging.basicConfig(level=logging.INFO)
import random

bot = Bot(token=token)
dp = Dispatcher(bot)

conn = sqlite3.connect('ananim.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username VARCHAR(200),
        chat_id INTEGER
    )
''')
conn.commit()

waiting_users = []


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM users WHERE user_id = {message.from_user.id};")
        res = cursor.fetchall()
        user_id = message.from_user.id
        if not res:
            cursor.execute(f"""INSERT INTO users (user_id, username, chat_id) VALUES (
                {message.from_user.id},
                '{message.from_user.username}',
                NULL
            );
            """)
            conn.commit()
            print(f"User {message.from_user.username} with ID {message.from_user.id} registered.")
        await message.answer("Добро пожаловать в анонимный чат! Вы зарегистрированы\n"
                             "Для помощи используйте /help")
    except Exception as e:
        print(f"Error: {e}")


@dp.message_handler(commands=['next'])
async def next_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id in waiting_users:
        waiting_users.remove(user_id)

    cursor.execute('UPDATE users SET chat_id = NULL WHERE user_id = ?', (user_id,))
    conn.commit()

    await message.answer("Поиск нового собеседника...")
    await find_partner(user_id)

async def find_partner(user_id):
    if waiting_users:
        partner_id = random.choice(waiting_users)
        waiting_users.remove(partner_id)
        cursor.execute('UPDATE users SET chat_id = ? WHERE user_id IN (?, ?)',
                       (user_id, user_id, partner_id))
        conn.commit()

        await bot.send_message(user_id, "Собеседник найден! Начните общение.")
        await bot.send_message(partner_id, "Собеседник найден! Начните общение.")
    else:
        waiting_users.append(user_id)
        await bot.send_message(user_id, "Ожидаем подключения собеседника. Пожалуйста, подождите...")


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await message.reply("Доступные команды:\n"
                        "/start - начать чат\n"
                        "/next - завершить текущий чат и начать поиск нового собеседника\n"
                        "/help - вывести список доступных команд")

@dp.message_handler(content_types=types.ContentType.ANY)
async def handle_messages(message: types.Message):
    user_id = message.from_user.id

    cursor.execute('SELECT chat_id FROM users WHERE user_id = ?', (user_id,))
    chat_id = cursor.fetchone()[0]

    if not chat_id:
        await message.reply("Пожалуйста, используйте команду /start, чтобы начать чат. "
                            "Для помощи используйте /help")
        return

    await bot.send_message(chat_id, f"Аноним: {message.text}")



executor.start_polling(dp, skip_updates=True)
