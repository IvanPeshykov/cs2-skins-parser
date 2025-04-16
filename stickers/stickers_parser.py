import asyncio
from stickers import stickers
import requests

class StickersParser:

    def __init__(self, skin_item):
        self.skin_item = skin_item
        self.stickers = self.find_stickers(skin_item)

    @staticmethod
    def is_valid(skin_item):
        return len(skin_item['descriptions']) >= 7 and StickersParser.find_stickers(skin_item) is not None

    @staticmethod
    def find_stickers(skin_item):
        for description in skin_item['descriptions']:
            if description['name'] == 'sticker_info':
                return description['value']

        return None


    async def get_sticker_price(self, url):
        html = requests.get(url)
        return stickers.find_price(html.text)

    async def parse(self):
        titles = stickers.get_titles(self.stickers)

        for title in titles:
            price = await self.get_sticker_price(stickers.get_sticker_url(title))
            if price == -1:
                continue



            await asyncio.sleep(5)
