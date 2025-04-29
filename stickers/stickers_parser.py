import asyncio
import logging
from parser import Parser
from data import config
from stickers import stickers

class StickersParser(Parser):

    def __init__(self, proxy_manager, session, skin_item, revenue_price, db):
        super().__init__(proxy_manager)
        self.skin_item = skin_item
        self.session = session
        self.stickers = self.find_stickers(skin_item)
        self.revenue_price = revenue_price
        self.db = db

    @staticmethod
    def is_valid(skin_item):
        return len(skin_item['descriptions']) >= 6 and StickersParser.find_stickers(skin_item) is not None

    @staticmethod
    def find_stickers(skin_item):
        for description in skin_item['descriptions']:
            if description['name'] == 'sticker_info':
                return description['value']

        return None

    async def get_sticker_price(self, url):
        html = await self.fetch(url, config.STICKER_SLEEP_TIME)
        return self.get_item_price(html)

    async def parse(self):
        titles = stickers.get_titles(self.stickers)

        # Check if there are at least 4 stickers for them to be counted as identical
        consistent_stickers = 1
        total_price = 0
        consistent_price = 0

        for i, title in enumerate(titles):

            logging.info("Parsing sticker: " + title)

            price = self.db.get_sticker_price(title)

            if price is None:
                price = await self.get_sticker_price(stickers.get_sticker_url(title))
                self.db.add_sticker(title, price)

            if price == -1:
                continue

            # Check if the sticker is identical
            if i >= 1 and titles[i - 1] == title:
                consistent_stickers += 1
                consistent_price += price

            total_price += price

        is_identical = consistent_stickers >= 4

        if total_price > self.revenue_price[0] or consistent_price > self.revenue_price[1] and is_identical:
            logging.info("Stickers price: " + str(round(total_price)))
            return [True, total_price, is_identical]

        return [False, total_price, is_identical]