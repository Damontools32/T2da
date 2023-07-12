import os
from pydub import AudioSegment
import speech_recognition as sr
from telegram import Update, Voice
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Please send your voice message.')

def voice_to_text(update: Update, context: CallbackContext):
    voice: Voice = update.message.voice
    file = context.bot.get_file(voice.file_id)
    file.download('voice.ogg')

    ogg_audio = AudioSegment.from_ogg('voice.ogg')
    ogg_audio.export('voice.wav', format='wav')

    r = sr.Recognizer()
    with sr.AudioFile('voice.wav') as source:
        audio = r.record(source)

    try:
        recognized_text = r.recognize_sphinx(audio, language='fa')
        update.message.reply_text(recognized_text)
    except sr.UnknownValueError:
        update.message.reply_text("Unfortunately, I couldn't recognize the speech.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, voice_to_text))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
