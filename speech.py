import json
import os
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

model = Model("model-fa")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('Please send your voice message.')

@dp.message_handler(content_types=['voice'])
async def voice_to_text(message: types.Message):
    voice = message.voice
    file_path = await bot.get_file(voice.file_id)
    await bot.download_file(file_path.file_path, 'voice.ogg')

    ogg_audio = AudioSegment.from_ogg('voice.ogg')
    ogg_audio.export('voice.wav', format='wav')

    recognizer = KaldiRecognizer(model, 16000)

    with open('voice.wav', 'rb') as audio_file:
        while True:
            data = audio_file.read(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                recognized_text = result.get('text', '')
                await message.reply(recognized_text)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
