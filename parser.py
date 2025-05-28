import asyncio
from abc import ABC, abstractmethod
import json
import re
import logging
from data import config

# Base abstract class for parsers
class Parser(ABC):

    def __init__(self, proxy_manager):
        self.session = None
        self.proxy_manager = proxy_manager
        self.pause = False

    @abstractmethod
    def parse(self):
        pass

    def get_item_autobuy_price(self, html):
        match = re.search('var line1\s*=\s*(\[\[.*?\]\]);', html)

        if match:
            line1_data = match.group(1)
            try:
                # Ensure all elements are JSON-safe
                data = json.loads(line1_data.replace("'", '"'))
                # Get price
                return float(data[-1][1])
            except json.JSONDecodeError as e:
                logging.error("Failed to parse JSON:", e)
                return -1
        else:
            logging.warning("Iterm price not found." + html)
            return -1

    def get_item_sell_amount(self, html):
        match = re.search('var line1\s*=\s*(\[\[.*?\]\]);', html)

        if match:
            line1_data = match.group(1)
            try:
                # Ensure all elements are JSON-safe
                data = json.loads(line1_data.replace("'", '"'))
                # Get sell amount
                return int(data[-1][2])
            except json.JSONDecodeError as e:
                logging.error("Failed to parse JSON:", e)
                return -1
        else:
            logging.warning("Iterm sell amount not found." + html)
            return -1

    async def fetch(self, url, cooldown):

        if config.USE_PROXY:
            return await self.fetch_proxy(url, cooldown)
        else:
            return await self.fetch_no_proxy(url)

    async def fetch_proxy(self, url, cooldown):
        proxy = await self.proxy_manager.get_proxy()
        async with self.session.get(url, proxy=proxy) as response:
            if response.status == 200:
                await self.proxy_manager.schedule_release(proxy, cooldown)
                return await response.text()
            else:
                if response.status == 429:
                    await self.proxy_manager.schedule_release(proxy, config.TOO_MANY_REQUESTS_COOLDOWN)
                    raise Exception("Rate limit exceeded! Scheduling proxy " + proxy + "!")
                else:
                    await self.proxy_manager.schedule_release(proxy, 1)
                    logging.error(f"Failed to fetch {url}: {response.status}")
                return None

    async def fetch_no_proxy(self, url):
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                if response.status == 429:
                    raise Exception("Rate limit exceeded!")
                else:
                    logging.error(f"Failed to fetch {url}: {response.status}")
                return None

