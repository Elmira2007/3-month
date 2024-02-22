from aiogram import Bot, Dispatcher, types, executor
from config import token 

bot = Bot(token=token)
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer("Привет мир")

@dp.message_handler(commands='help')
async def help(message:types.Message):
    await message.answer("Чем могу помочь?")

@dp.message_handler(text="Привет")
async def hello(message:types.Message):
    await message.answer("Привет, как дела?")

@dp.message_handler(commands='test')
async def test(message:types.Message):
    await message.answer("Тестовый ответ")
    await message.answer_location(40.51931846586533, 72.80297788183063)
    await message.answer_photo('https://st-1.akipress.org/st_runews/.storage/limon3/images/JUNE2023/da00bdd997afbfe063630e32bbdedae0.jpg')
    with open('mirbek.mp3', 'rb') as music:
        await message.answer_audio(music)
    await message.answer_contact('+996772343206', 'Toktorov', 'Kurmanbek')
    await message.answer_dice()
    print(message)
    await message.answer(f"Здраствуйте {message.from_user.full_name}")

@dp.message_handler()
async def not_found(message:types.Message):
    await message.reply("Я вас не понял, введите /help")

executor.start_polling(dp)