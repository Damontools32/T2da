from telethon.sync import TelegramClient

api_id = 12345  # Replace with your API ID
api_hash = 'YOUR_API_HASH'
phone_number = '+1234567890'  # Replace with your phone number

with TelegramClient(None, api_id, api_hash) as client:
    print(client.session.save())
```

این کد را اجرا کنید و کد تأییدی را که به شماره تلفن شما ارسال می‌شود را وارد کنید. سپس رشته‌ای که چاپ می‌شود را در `SESSION_STRING` در فایل اصلی قرار دهید.￼Enter
