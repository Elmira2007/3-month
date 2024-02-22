from aiogram import Bot, Dispatcher, types, executor
from logging import basicConfig, INFO
from config import token 
import requests, os, time 

bot = Bot(token=token)
dp = Dispatcher(bot)
basicConfig(level=INFO)

@dp.message_handler(commands='start')
async def start(message:types.Message):
    await message.answer(f"Привет {message.from_user.full_name}")

@dp.message_handler()
async def send_tiktok_video(message:types.Message):
    if 'tiktok.com' in message.text:
        await message.answer("Начинаю скачивать видео...")
        input_url = message.text.split('/')
        print(input_url)
        current_id = input_url[5].split('?')[0]
        print(current_id)
        video_api = requests.get(f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={current_id}').json()
        # print(video_api)
        video_url = video_api.get('aweme_list')[0].get('video').get('play_addr').get('url_list')[0]
        print(video_url)
        if video_url:
            title = video_api.get('aweme_list')[0].get('aweme_id')
            try:
                os.mkdir('video')
            except:
                pass
            try:
                with open(f'video/{title}.mp4', 'wb') as video_file:
                    video_file.write(requests.get(video_url).content)
                await message.answer(f'Видео {title} успешно скачан')
                with open(f'video/{title}.mp4', 'rb') as read_video_file:
                    await message.answer_video(read_video_file)
                os.remove(f'video/{title}.mp4')
            except Exception as error:
                await message.answer(f"Error {error}")
    else:
        await message.answer("Неправильная ссылка на видео")

executor.start_polling(dp)