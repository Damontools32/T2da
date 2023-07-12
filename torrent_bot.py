import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from torrentool.api import Torrent

API_ID = "20307429"
API_HASH = 'db1b2a38958c06bc4e99b01d4cfd485d'
SESSION_STRING = '...'
TELEGRAM_APP_NAME = 'Remote'
TELEGRAM_API_TOKEN = '6213454948:AAG1Sv1lyiOYqkOnR0KpYSbfnjRsyKwk8pl'
DOWNLOAD_DIR = 'downloads'

client = Client("my_account", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
selected_files = {}

files = []


@client.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("Send me a torrent file and I'll help you download it.")


@client.on_message(filters.document)
async def handle_torrent(_, message):
    global files
    file = await message.download(file_name="temp.torrent")
    torrent = Torrent.from_file(file)
    os.remove("temp.torrent")

    files = torrent.files

    keyboard = [
        [
            InlineKeyboardButton(
                f"{i}: {file.path}", callback_data=f"file_selection_{i}"
            )
            for i, file in enumerate(files)
        ],
        [
            InlineKeyboardButton("Select All", callback_data="select_all"),
            InlineKeyboardButton("Deselect All", callback_data="deselect_all"),
        ],
        [InlineKeyboardButton("Start Download", callback_data="start_download")],
    ]

    text = "Select the files you want to download by clicking on them:"
    await message.reply(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


@client.on_callback_query(filters.regex("^(file_selection|select_all|deselect_all)"))
async def handle_file_selection(_, callback_query: CallbackQuery):
    data = callback_query.data
    message_id = callback_query.message.message_id

    if message_id not in selected_files:
        selected_files[message_id] = []

    if data.startswith("file_selection"):
        file_index = int(data.split("_")[-1])

        if file_index in selected_files[message_id]:
            selected_files[message_id].remove(file_index)
        else:
            selected_files[message_id].append(file_index)
    elif data == "select_all":
        selected_files[message_id] = list(range(len(files)))
    elif data == "deselect_all":
        selected_files[message_id] = []

    text = "Select the files you want to download by clicking on them:"
    await callback_query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    await callback_query.answer()


@client.on_callback_query(filters.regex("^start_download"))
async def handle_download_start(_, callback_query: CallbackQuery):
    message_id = callback_query.message.message_id

    if message_id not in selected_files or not selected_files[message_id]:
        await callback_query.answer("No files selected!", show_alert=True)
        return

    await callback_query.answer("Downloading...")

    # Download the selected files
    for file_index in selected_files[message_id]:
        file = files[file_index]
        await file.download(DOWNLOAD_DIR)

    del selected_files[message_id]

    await callback_query.message.edit("Download complete!")


client.run()
