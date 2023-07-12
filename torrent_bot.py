import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from torrentool.api import Torrent

API_ID = "YOUR_API_ID"
API_HASH = 'YOUR_API_HASH'
BOT_TOKEN = 'YOUR_BOT_TOKEN'
DOWNLOAD_DIR = 'downloads'

client = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

selected_files = {}
files = []


@client.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("Send me a torrent file and I'll help you download it.")


@client.on_message(filters.document)
async def handle_document(_, message):
    if message.document.file_name.endswith(".torrent"):
        torrent_file = await message.download(file_name="downloads/")
        torrent = Torrent.from_file(torrent_file)
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Select All", callback_data="select_all")],
            *[[InlineKeyboardButton(f"{i+1}. {file.name}", callback_data=f"{i}")] for i, file in enumerate(torrent.files)],
            [InlineKeyboardButton("Download", callback_data="download")]
        ])
        
        await message.reply(f"Torrent info:\n\n"
                            f"Name: {torrent.name}\n"
                            f"Size: {torrent.total_size} bytes\n\n"
                            f"Select files to download:",
                            reply_markup=markup)
    else:
        await message.reply("Please send a valid .torrent file.")


@client.on_callback_query()
async def handle_callback_query(client: Client, query: CallbackQuery):
    index = query.data
    
    if index == "select_all":
        for i, _ in enumerate(files):
            selected_files[i] = True
    elif index == "download":
        # TODO: Add your download logic here
        pass
    else:
        index = int(index)
        if index in selected_files:
            del selected_files[index]
        else:
            selected_files[index] = True
    
    await query.answer()


client.run()
