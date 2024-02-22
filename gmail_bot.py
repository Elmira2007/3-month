from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from logging import basicConfig, INFO
from email.message import EmailMessage
from config import token, smtp_sender, smtp_sender_password
import smtplib

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
basicConfig(level=INFO)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer(f'{message.from_user.full_name}. Введите /mail - для отправки электронной почты')

class MailState(StatesGroup):
    email = State()
    title = State()
    message = State()

@dp.message_handler(commands='mail')
async def start_send_mail(message:types.Message):
    await message.answer("На какую почту вы хотите отправить сообщение?")
    await MailState.email.set()

@dp.message_handler(state=MailState.email)
async def get_title_mail(message:types.Message, state:FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Заголовок вашего сообщения:")
    await MailState.title.set()

@dp.message_handler(state=MailState.title)
async def get_message_mail(message:types.Message, state:FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите ваше сообщение:")
    await MailState.message.set()

@dp.message_handler(state=MailState.message)
async def end_send_mail(message:types.Message, state:FSMContext):
    await state.update_data(message=message.text)
    await message.answer("Начинаю отправку почты")
    result = await storage.get_data(user=message.from_user.id)
    sender = smtp_sender
    password = smtp_sender_password

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    msg = EmailMessage()
    msg.set_content(result['message'])

    msg['Subject'] = result['title'] 
    msg['From'] = sender 
    msg['To'] = result['email']

    try:
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        await message.answer("Почта успешно отправлена")
    except Exception as error:
        await message.answer(f"Ошибка: {error}")

executor.start_polling(dp, skip_updates=True)