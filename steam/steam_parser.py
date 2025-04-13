import requests
from skins import skins
from stickers.stickers_parser import StickersParser

class SteamParser:

        async def start_parsing(self):
            await self.parse_url("https://steamcommunity.com/market/listings/730/AWP%20%7C%20Sun%20in%20Leo%20(Field-Tested)")
            # for skin in skins.get_all_names():
            #     url = skins.get_skin_url(skin)
            #     await self.parse_url(url)

        async def parse_url(self, url):
            html = requests.get("https://steamcommunity.com/market/listings/730/AWP%20%7C%20Sun%20in%20Leo%20(Field-Tested)")
            items = skins.get_assets(html.text)

            for item in items:
                skin_item = items[item]

                if not StickersParser.is_valid(skin_item):
                    continue

                stickers_parser = StickersParser(skin_item)
                stickers_parser.parse()



