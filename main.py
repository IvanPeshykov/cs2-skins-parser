import os.path
from steam.steam_parser import SteamParser
import asyncio
import logging
from misc.proxy_manager import ProxyManager

def load_proxies():
    with open("data/proxies.txt") as f:
        proxies = f.read().splitlines()
        return proxies

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

def main():

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
    proxy_manager = ProxyManager(load_proxies())
    parser = SteamParser(proxy_manager)
    # Start the parsing process
    asyncio.run(parser.parse())

if __name__ == "__main__":
    main()