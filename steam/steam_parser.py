import asyncio
from parser import Parser
from skins import skins
from data import config
from stickers import stickers_db
from stickers.stickers_parser import StickersParser
import logging
import aiohttp


class SteamParser(Parser):

        def __init__(self, proxy_manager):
            super().__init__(proxy_manager)
            self.db = None

        async def parse(self):
            # Limit concurrent requests
            semaphore = asyncio.Semaphore(config.THREADS_NUM)

            self.db = stickers_db.StickersDB()

            async def parse_limited(skin):
                async with semaphore:
                    url = skins.get_skin_url(skin)
                    return await self.parse_url(url)

            async with aiohttp.ClientSession() as session:
                self.session = session
                tasks = [parse_limited(skin) for skin in skins.get_all_names()]
                await asyncio.gather(*tasks)

        async def parse_url(self, url):
            try:
                logging.info("Parsing URL: " + url)
                html = await self.fetch(url, config.SKIN_SLEEP_TIME)
                items = skins.get_assets(html)

                skin_price = self.get_item_price(html)
                revenue_price = skins.get_revenue_price(skin_price)

                for i, item in enumerate(items):

                    skin_item = items[item]
                    skin_price = self.get_item_price(html)

                    if skin_price  == -1:
                        continue

                    if not StickersParser.is_valid(skin_item):
                        continue

                    stickers_parser = StickersParser(self.proxy_manager, self.session, skin_item, revenue_price, self.db)
                    should_buy = await stickers_parser.parse()

                    if should_buy:
                        logging.info("You should buy: " + url + "with index: " + str(i))
                        logging.info("Skin price: " + str(round(skin_price)))

                logging.info("Finished parsing URL: " + url)

            except Exception as e:
                logging.error(f"Error parsing URL {url}: {e}")




