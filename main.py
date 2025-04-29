import os.path
from steam.steam_parser import SteamParser
import asyncio
import logging
from misc.proxy_manager import ProxyManager
from fastapi import FastAPI
import uvicorn

app = FastAPI()

def load_proxies():
    with open("data/proxies.txt") as f:
        proxies = f.read().splitlines()
        return proxies

proxy_manager = ProxyManager(load_proxies())
parser = SteamParser(proxy_manager)

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

def setup_logging():
    logname = 'parser.log'

    # Create logger
    logger = logging.getLogger('parser')
    logger.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # File handler
    file_handler = logging.FileHandler(logname, mode='a')
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handlers if not already added
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

async def main():

    # Clear log
    if os.path.isfile('debug.log'):
        os.remove('debug.log')

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )


    logging.info("Starting the parser...")
    # Start the parsing process
    await asyncio.gather(
        start_uvicorn(),
        parser.parse()
    )

if __name__ == "__main__":
    asyncio.run(main())