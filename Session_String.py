from telethon.sync import TelegramClient

api_id = 12345  # Replace with your API ID
api_hash = 'YOUR_API_HASH'
phone_number = '+1234567890'  # Replace with your phone number

with TelegramClient(None, api_id, api_hash) as client:
    print(client.session.save())
