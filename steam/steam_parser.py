import asyncio
import traceback
from parser import Parser
from skins import skins
from data import config
from stickers import stickers_db
from stickers.stickers_parser import StickersParser
from misc import telegram_bot
import logging
import aiohttp
import random
from dotenv import load_dotenv

load_dotenv()


class SteamParser(Parser,):

        def __init__(self, proxy_manager):
            super().__init__(proxy_manager)
            self.db = None
            self.lock = asyncio.Lock()
            self.sent_messages = set()

        async def parse(self):
            self.db = stickers_db.StickersDB()

            queue = asyncio.Queue()

            async with aiohttp.ClientSession() as session:
                self.session = session

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

                autobuy_price = self.get_item_autobuy_price(html)
                skin_sell_amount = self.get_item_sell_amount(html)
                if autobuy_price < config.MIN_PRICE or autobuy_price > config.MAX_PRICE or skin_sell_amount <= config.MIN_SELL_AMOUNT:
                    await self.write_wrong_skin(skin_name)

                for i, skin_id in enumerate(items):

                    skin_price = skins.get_price(html, i, autobuy_price)
                    skin_item = items[skin_id]
                    revenue_price = skins.get_revenue_price(skin_price)

                    if skin_price  == -1:
                        continue

                    if not StickersParser.is_valid(skin_item):
                        continue


                    stickers_parser = StickersParser(self.proxy_manager, self.session, skin_item, revenue_price, self.db)
                    [should_buy, sticker_price, consistent_price, is_stickers_identical, stickers_text] = await stickers_parser.parse()

                    if should_buy:

                        profit = skins.calculate_profit(skin_price, sticker_price, consistent_price, is_stickers_identical)

                        # Fee percentage in steam is 15%
                        fee_profit = profit - abs(profit * 0.15)

                        unique_message = skins.skin_success_text(skin_url=url, skin_name=skin_name, price=skin_price,
                                                                                    autobuy_price=autobuy_price, profit=profit, steam_profit=fee_profit, stickers_price=sticker_price, stickers_text=stickers_text, position=i)
                        if unique_message not in self.sent_messages:
                            logging.info("Found skin " + skin_name + " with price " + str(skin_price) + "$")
                            action_url = skins.get_action_url(skin_item, skin_id)
                            screenshot_url =  await self.generate_screenshot(action_url)
                            await telegram_bot.send_message(unique_message, image_url=screenshot_url)

                        self.sent_messages.add(unique_message)

                logging.info("Finished parsing URL: " + url)

            except Exception as e:
                if config.DEBUG:
                    logging.error(traceback.format_exc())
                logging.error(f"Error parsing URL {url}:\n{e}")

        async def write_wrong_skin(self, skin_name):
            async with self.lock:
                with open("data/wrong.txt", "a") as f:
                    f.write(f"{skin_name}\n")

        async def generate_screenshot(self, action_url):
            url = 'https://api.swap.gg/v2/screenshot'
            payload = {"inspectLink": action_url}
            proxy = await self.proxy_manager.get_proxy()

            for attempt in range(3):
                async with self.session.post(url, json=payload, proxy=proxy) as response:
                    try:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('state', '') == 'IN_QUEUE':
                                await asyncio.sleep(5)
                                continue
                            screenshot_id = data.get('result').get('imageId')
                            await self.proxy_manager.schedule_release(proxy, 1)
                            return f'https://s.swap.gg/{screenshot_id}.jpg'
                        else:
                            logging.error(f"Failed to generate screenshot for {action_url}: {response.status}")
                            await self.proxy_manager.schedule_release(proxy, 1)
                            return None
                    except Exception as e:
                        await self.proxy_manager.schedule_release(proxy, 1)

            await self.proxy_manager.schedule_release(proxy, 1)


