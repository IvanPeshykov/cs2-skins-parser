import asyncio
from parser import Parser
from skins import skins
from data import config
from stickers import stickers_db
from stickers.stickers_parser import StickersParser
from misc import telegram_bot
import logging
import aiohttp
import random

class SteamParser(Parser):

        def __init__(self, proxy_manager):
            super().__init__(proxy_manager)
            self.db = None
            self.lock = asyncio.Lock()
            self.sent_messages = set()

        async def parse(self):
            queue = asyncio.Queue()

            async with aiohttp.ClientSession() as session:
                self.session = session
                self.db = stickers_db.StickersDB()

                for skin in skins.get_all_names():
                    await queue.put(skin)

                async def worker():
                    while True:
                        if self.pause:
                            await asyncio.sleep(1)
                            continue

                        skin = await queue.get()
                        await queue.put(skin)
                        url = skins.get_skin_url(skin)
                        await self.parse_url(url, skin)
                        queue.task_done()

                # Start workers
                workers = [asyncio.create_task(worker()) for _ in range(config.THREADS_NUM)]

                await asyncio.gather(*workers)  # Keep main task alive

        async def parse_url(self, url, skin_name):
            try:
                logging.info("Parsing URL: " + url)
                html = await self.fetch(url, random.randint(config.SKIN_SLEEP_TIME_MIN, config.SKIN_SLEEP_TIME_MAX))
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

                        if unique_message not in self.sent_messages:
                            await telegram_bot.send_message("You should buy: " + url + " with index: " + str(i) + ". Skin price - " + skin_price_str + "$"\
                                                        + " and sticker price - " + sticker_price_str + "$. Stickers identical: " + str(is_stickers_identical))

                        self.sent_messages.add(unique_message)

                logging.info("Finished parsing URL: " + url)

            except Exception as e:
                logging.error(f"Error parsing URL {url}: {e}")

        async def write_wrong_skin(self, skin_name):
            async with self.lock:
                with open("data/wrong.txt", "a") as f:
                    f.write(f"{skin_name}\n")




