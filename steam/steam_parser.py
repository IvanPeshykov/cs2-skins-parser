import asyncio
from parser import Parser
from skins import skins
from data import config
from stickers import stickers_db
from stickers.stickers_parser import StickersParser
from misc import telegram_bot
import logging
import aiohttp


class SteamParser(Parser):

        def __init__(self, proxy_manager):
            super().__init__(proxy_manager)
            self.db = None
            self.lock = asyncio.Lock()
            self.sent_mesages = set()


        async def parse(self):
            # Limit concurrent requests
            semaphore = asyncio.Semaphore(config.THREADS_NUM)

            self.db = stickers_db.StickersDB()

            async def parse_limited(skin):
                async with semaphore:
                    url = skins.get_skin_url(skin)
                    return await self.parse_url(url, skin)

            async with aiohttp.ClientSession() as session:
                self.session = session
                while True:
                    tasks = [parse_limited(skin) for skin in skins.get_all_names()]
                    await asyncio.gather(*tasks)

        async def parse_url(self, url, skin_name):
            try:
                logging.info("Parsing URL: " + url)
                html = await self.fetch(url, config.SKIN_SLEEP_TIME)
                items = skins.get_assets(html)

                if items == -1:
                    await self.write_wrong_skin(skin_name)
                    return

                skin_price = self.get_item_price(html)
                skin_sell_amount = self.get_item_sell_amount(html)
                revenue_price = skins.get_revenue_price(skin_price)

                if skin_price < config.MIN_PRICE or skin_price > config.MAX_PRICE or skin_sell_amount <= config.MIN_SELL_AMOUNT:
                    await self.write_wrong_skin(skin_name)

                for i, item in enumerate(items):

                    skin_item = items[item]

                    if skin_price  == -1:
                        continue

                    if not StickersParser.is_valid(skin_item):
                        continue

                    stickers_parser = StickersParser(self.proxy_manager, self.session, skin_item, revenue_price, self.db)
                    [should_buy, sticker_price, is_stickers_identical] = await stickers_parser.parse()

                    if should_buy:

                        skin_price_str = str(round(skin_price))
                        sticker_price_str = str(round(sticker_price))

                        unique_message = url + skin_price_str + sticker_price_str

                        if unique_message not in self.sent_mesages:
                            await telegram_bot.send_message("You should buy: " + url + " with index: " + str(i) + ". Skin price - " + skin_price_str + "$"\
                                                        + " and sticker price - " + sticker_price_str + "$. Stickers identical: " + str(is_stickers_identical))

                        self.sent_mesages.add(unique_message)

                logging.info("Finished parsing URL: " + url)

            except Exception as e:
                logging.error(f"Error parsing URL {url}: {e}")

        async def write_wrong_skin(self, skin_name):
            async with self.lock:
                with open("data/wrong.txt", "a") as f:
                    f.write(f"{skin_name}\n")




