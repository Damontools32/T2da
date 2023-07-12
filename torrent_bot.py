import os
import tempfile
import libtorrent as lt
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument

API_ID = 12345  # Replace with your API ID
API_HASH = 'YOUR_API_HASH'
SESSION_STRING = 'YOUR_SESSION_STRING'
TELEGRAM_APP_NAME = 'your_app_name'  # Replace with your app name
TELEGRAM_API_TOKEN = 'YOUR_TELEGRAM_API_TOKEN'  # Replace with your Telegram API token
DOWNLOAD_DIR = 'downloads'

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
client.start()

app = Client(TELEGRAM_APP_NAME, API_ID, API_HASH, bot_token=TELEGRAM_API_TOKEN)

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Please send me a torrent file.")


@app.on_message(filters.document)
async def handle_torrent(client, message):
    if message.document.mime_type != "application/x-bittorrent":
        return

    torrent_file_path = os.path.join(DOWNLOAD_DIR, message.document.file_name)
    await message.download(file_name=torrent_file_path)

    ses = lt.session()
    info = lt.torrent_info(torrent_file_path)
    h = ses.add_torrent({'ti': info, 'save_path': DOWNLOAD_DIR})
    files = info.files()

    keyboard = [InlineKeyboardButton(f"{i}: {file.path}", callback_data=f"{i}") for i, file in enumerate(files)]
    reply_markup = InlineKeyboardMarkup([keyboard])

    await message.reply_text("Select the files you want to download:", reply_markup=reply_markup)

    message.__setattr__('torrent_handle', h)
    message.__setattr__('selected_files', set())


@app.on_callback_query()
async def handle_file_selection(client, callback_query):
    file_index = int(callback_query.data)

    if file_index in callback_query.message.selected_files:
        callback_query.message.selected_files.remove(file_index)
        text = "File deselected."
    else:
        callback_query.message.selected_files.add(file_index)
        text = "File selected."

    await callback_query.answer(text=text)


@app.on_message(filters.command("download"))
async def download_selected(client, message):
    selected_files = message.selected_files
    torrent_handle = message.torrent_handle

    if not selected_files or not torrent_handle:
        await message.reply_text("No files selected.")
        return

    torrent_handle.set_priority([1 if i in selected_files else 0 for i in range(torrent_handle.torrent_file().num_files())])

    await message.reply_text("Downloading files...")
    while not torrent_handle.is_seed():
        status = torrent_handle.status()
        progress = int(status.progress * 100)
        await message.reply_text(f"Download progress: {progress}%")
        await asyncio.sleep(5)

    await message.reply_text("Download complete. Uploading files...")

    for file_index in selected_files:
        file_path = torrent_handle.torrent_file().files()[file_index].path
        file_size = os.path.getsize(file_path)

        with open(file_path, 'rb') as file:
            if file_size > 2000000:
                await client.send_document(message.chat.id, document=file)
            else:
                await client.send_document(message.chat.id, document=InputMediaDocument(media=file))

    await message.reply_text("Upload complete.")


app.run()
