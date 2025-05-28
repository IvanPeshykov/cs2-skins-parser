import aiohttp
import logging

async def send_message(text, image_url=None):
    try:
        async with aiohttp.ClientSession() as session:
            if image_url:
                await session.post("http://telegram_bot:8000/send_message", json={"text": text, "image_url": image_url})
            else:
                await session.post("http://telegram_bot:8000/send_message", json={"text": text})

    except aiohttp.ClientError as e:
        logging.error(f"Error sending message to Telegram bot: {e}")
