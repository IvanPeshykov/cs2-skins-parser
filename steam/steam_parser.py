import asyncio
import requests
from parser import Parser
from skins import skins
from data import config
from stickers.stickers_parser import StickersParser
import logging

class SteamParser(Parser):

        async def parse(self):
            for skin in skins.get_all_names():
                url = skins.get_skin_url(skin)
                await self.parse_url(url)
                await asyncio.sleep(config.SKIN_SLEEP_TIME)

        async def parse_url(self, url):
            logging.info("Parsing URL: " + url)

            html = requests.get(url)
            items = skins.get_assets(html.text)

            for i, item in enumerate(items):

                logging.info("Parsing skin with index: " + str(i))

                skin_item = items[item]
                skin_price = self.get_item_price(html.text)

                if skin_price  == -1:
                    continue

                revenue_price = skins.get_revenue_price(skin_price)

                if not StickersParser.is_valid(skin_item):
                    continue

                stickers_parser = StickersParser(skin_item, revenue_price)
                should_buy = await stickers_parser.parse()

                if should_buy:
                    logging.info("You should buy: " + url + "with index: " + str(i))
                    logging.info("Skin price: " + str(round(skin_price)))

                await asyncio.sleep(config.SKIN_SLEEP_TIME)



