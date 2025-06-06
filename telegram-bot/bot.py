import asyncio
import aiohttp
import requests
from telegram import Bot
from fastapi import FastAPI, Request
import logging
import os
from dotenv import load_dotenv
import uvicorn
from io import BytesIO

# Telegram bot configuration

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
user_chat_id = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token)
app = FastAPI()


async def start_uvicorn():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

@app.post("/send_message")
async def send_message_req(request: Request):
    data = await request.json()

    message_text = data.get("text", "")
    image_url = data.get("image_url", None)

    logging.info(f"Received message: {message_text}")
    await send_message(user_chat_id, message_text, image_url)

async def send_message(chat_id, text, image_url=None):
    # Send a message to the Telegram bot with optional image
    try:
        if image_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    response.raise_for_status()
                    image_data = BytesIO(await response.read())
                    await bot.send_photo(chat_id=chat_id, photo=image_data, caption=text, parse_mode='HTML')
        else:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')

async def pause_parser(chat_id):
    requests.post("http://steam_parser:8001/pause")
    await bot.send_message(chat_id = chat_id, text="Parser paused.")

async def resume_parser(chat_id):
    requests.post("http://steam_parser:8001/resume")
    await bot.send_message(chat_id = chat_id, text="Parser resumed.")


async def parse_updates():
    # Parse updates to handle commands from user
    try:
            while True:
                await asyncio.sleep(30)
                updates = await bot.get_updates()
                update = updates[len(updates) - 1]
                if update.message:
                    text = update.message.text
                    chat_id = update.message.chat_id

                    if chat_id != int(user_chat_id):
                        continue

                    try:
                        await bot.delete_message(chat_id=user_chat_id, message_id=update.message.message_id)
                    except:
                        continue

                    if text == '/pause':
                        await pause_parser(user_chat_id)

                    elif text == '/resume':
                        await resume_parser(user_chat_id)

    except Exception as e:
        logging.error(f"Error in parse_updates: {e}")

async def main():
    await asyncio.gather(
        start_uvicorn(),
        parse_updates()
    )


if __name__ == '__main__':
    asyncio.run(main())




