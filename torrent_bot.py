import os
import tempfile
import libtorrent as lt
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
API_ID = 12345  # Replace with your API ID
API_HASH = 'YOUR_API_HASH'
SESSION_STRING = 'YOUR_SESSION_STRING'
DOWNLOAD_DIR = 'downloads'

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
client.start()

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Please send me a torrent file.')


def handle_torrent(update: Update, context: CallbackContext):
    file_id = update.message.document.file_id
    new_file = context.bot.get_file(file_id)
    torrent_file_path = os.path.join(DOWNLOAD_DIR, new_file.file_path.split('/')[-1])

    new_file.download(torrent_file_path)

    ses = lt.session()
    info = lt.torrent_info(torrent_file_path)
    h = ses.add_torrent({'ti': info, 'save_path': DOWNLOAD_DIR})
    files = info.files()

    keyboard = [InlineKeyboardButton(f"{i}: {file.path}", callback_data=f"{i}") for i, file in enumerate(files)]
    reply_markup = InlineKeyboardMarkup.from_column(keyboard)

    update.message.reply_text("Select the files you want to download:", reply_markup=reply_markup)

    context.user_data["torrent_handle"] = h
    context.user_data["selected_files"] = set()


def handle_file_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    file_index = int(query.data)

    if file_index in context.user_data["selected_files"]:
        context.user_data["selected_files"].remove(file_index)
        text = "File deselected."
    else:
        context.user_data["selected_files"].add(file_index)
        text = "File selected."

    query.answer(text=text)


def download_selected(update: Update, context: CallbackContext):
    selected_files = context.user_data.get("selected_files")
    torrent_handle = context.user_data.get("torrent_handle")

    if not selected_files or not torrent_handle:
        update.message.reply_text("No files selected.")
        return

    torrent_handle.set_priority([1 if i in selected_files else 0 for i in range(torrent_handle.torrent_file().num_files())])

    update.message.reply_text("Downloading files...")
    while not torrent_handle.is_seed():
        status = torrent_handle.status()
        progress = int(status.progress * 100)
        update.message.reply_text(f"Download progress: {progress}%")
        time.sleep(5)

    update.message.reply_text("Download complete. Uploading files...")

    for file_index in selected_files:
        file_path = torrent_handle.torrent_file().files()[file_index].path
        file_size = os.path.getsize(file_path)

        with open(file_path, 'rb') as file:
            if file_size > 2000000:
                asyncio.run(client.send_file(update.message.chat.id, file))
            else:
                context.bot.send_document(chat_id=update.message.chat.id, document=InputFile(file))

    update.message.reply_text("Upload complete.")


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/x-bittorrent"), handle_torrent))
dispatcher.add_handler(CallbackQueryHandler(handle_file_selection))
dispatcher.add_handler(CommandHandler('download', download_selected))

updater.start_polling()
updater.idle()
