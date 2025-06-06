import os.path
from steam.steam_parser import SteamParser
from steam.steam_currency import SteamCurrencyExchanger
import asyncio
import logging
from misc.proxy_manager import ProxyManager
from fastapi import FastAPI
import uvicorn
import random
from misc import telegram_bot


def load_proxies():
    with open("data/proxies.txt") as f:
        proxies = f.read().splitlines()
        return proxies

app = FastAPI()
proxy_manager = ProxyManager(load_proxies())
parser = SteamParser(proxy_manager)


# Start listening for incoming messages from bot
async def start_uvicorn():
    config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

@app.post("/pause")
async def pause_parser():
    # Pause the parser
    parser.pause = True
    logging.info("Parser paused.")

@app.post("/resume")
async def resume_parser():
    # Resume the parser
    parser.pause = False
    logging.info("Parser resumed.")

# Pauser function to randomly pause the parser
async def random_pauser():

    first_launch = True

    while True:
        if parser.pause:
            await asyncio.sleep(1)
            continue

        # Randomly pause the parser for a short time
        if random.random() < 0.1 and not first_launch:  # 10% chance to pause
            parser.pause = True
            pause_time = random.uniform(5, 1200)  # Random pause time between 5 and 1800 seconds
            await telegram_bot.send_message(f"Parser paused for {pause_time:.2f} seconds.")
            await asyncio.sleep(pause_time)
            parser.pause = False
            await telegram_bot.send_message("Parser resumed after random pause.")
            logging.info("Parser resumed after random pause.")

        first_launch = False
        await asyncio.sleep(random.uniform(200, 600))

async def main():

    # Clear log
    if os.path.isfile('debug.log'):
        os.remove('debug.log')

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )

    # Update currency JSON file
    SteamCurrencyExchanger.updateCurrencyJSONFile()

    logging.info("Starting the parser...")
    # Start pauser, parser and tg bot listener
    await asyncio.gather(
        start_uvicorn(),
        parser.parse(),
        random_pauser()
    )

if __name__ == "__main__":
    asyncio.run(main())