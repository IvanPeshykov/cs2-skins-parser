from steam.steam_parser import SteamParser
import asyncio
import  logging
from data import config
from misc.proxy_manager import ProxyManager

def load_proxies():
    with open("data/proxies.txt") as f:
        proxies = f.read().splitlines()
        return proxies

def main():

    logging.basicConfig(
        format="%(levelname)s | %(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger().setLevel(logging.INFO)
    logging.info("Starting the parser...")

    proxy_manager = ProxyManager(load_proxies())
    parser = SteamParser(proxy_manager)
    # Start the parsing process
    asyncio.run(parser.parse())

if __name__ == "__main__":
    main()