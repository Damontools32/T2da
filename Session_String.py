from telethon.sync import TelegramClient

api_id = 12345  # Replace with your API ID
api_hash = 'YOUR_API_HASH'
phone_number = '+1234567890'  # Replace with your phone number
session_file = 'my_session.session'  # Replace with your desired session file name

with TelegramClient(session_file, api_id, api_hash) as client:
    client.start(phone_number)
    print("Session string saved to:", session_file)
