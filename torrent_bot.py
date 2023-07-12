import os
import asyncio
import libtorrent as lt
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
torrent_file_id = None


@client.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("Send me a torrent file and I'll help you download it.")


@client.on_message(filters.document)
async def handle_document(_, message):
    global torrent_file_id
    if message.document.file_name.endswith(".torrent"):
        torrent_file = await message.download(file_name="downloads/")
        torrent = Torrent.from_file(torrent_file)

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Select All", callback_data="select_all")],
            *[[InlineKeyboardButton(f"{i + 1}. {file.name}", callback_data=f"{i}")] for i, file in enumerate(torrent.files)],
            [InlineKeyboardButton("Download", callback_data="download")]
        ])

        torrent_file_id = message.document.file_id

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
        # Download selected torrent files
        await download_torrent(query)
    else:
        index = int(index)
        if index in selected_files:
            del selected_files[index]
        else:
            selected_files[index] = True

    await query.answer()


async def download_torrent(query: CallbackQuery):
    global torrent_file_id
    message = query.message
    torrent_file_path = await client.download_media(torrent_file_id)

    ses = lt.session()
    with open(torrent_file_path, "rb") as f:
        info = lt.torrent_info(lt.bdecode(f.read()))

    params = {
        "save_path": DOWNLOAD_DIR,
        "ti": info,
        "flags": lt.torrent_flags.auto_managed,
    }

    handle = ses.add_torrent(params)

    for index, _ in enumerate(info.files()):
        handle.file_priority(index, 0 if index not in selected_files else 1)

    last_progress = None
    while True:
        s = handle.status()
        is_seed = (s.state == lt.torrent_status.seeding)  # Check if seeding instead of using is_seed()
        progress = s.progress * 100

        if not is_seed and progress != last_progress:
            await message.edit_text(f"Downloading: {progress:.2f}% - {s.download_rate / 1000:.2f} kB/s")
            last_progress = progress

        if is_seed:
            break

        await asyncio.sleep(1)

    await message.edit_text("Download complete! Now sending the files...")

    for index in selected_files:
        file_path = os.path.join(DOWNLOAD_DIR, info.files()[index].path)
        await message.reply_document(file_path)

    await message.edit_text("All files have been sent, the download folder will be cleared.")
    for index in selected_files:
        file_path = os.path.join(DOWNLOAD_DIR, info.files()[index].path)
        os.remove(file_path)
    os.remove(torrent_file_path)

client.run()
