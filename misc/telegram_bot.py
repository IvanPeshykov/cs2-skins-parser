import aiohttp
from data import config

BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
CHAT_ID = config.CHAT_ID
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

async def send_message(text: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            'chat_id': CHAT_ID,
            'text': text
        }
        async with session.post(API_URL, data=payload) as resp:
            print(f"Sent message, status: {resp.status}")
            return await resp.json()