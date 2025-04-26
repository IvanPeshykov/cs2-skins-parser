import json
import re
import logging
import urllib

def get_all_names():
    with open('data/marketplaceids.json', 'r', encoding="utf8") as f:
        names = json.load(f)
        return names['items'].keys()

def get_skin_url(skin_name: str) -> str:

    url = "https://steamcommunity.com/market/listings/730/"

    if "|" not in skin_name:
        parts = skin_name.split(' ', 1)
        if len(parts) == 2:
            name = f"{parts[0]} | {parts[1]}"
    else:
        # Normalize spacing around "|" to be " | "
        name = " | ".join(part.strip() for part in skin_name.split('|', 1))

    return url + urllib.parse.quote(skin_name)

def get_assets(html):
            # Regular expression to match the g_rgAssets variable and capture the object content
            pattern = r'var g_rgAssets = ({.*?});'

            # Search for the pattern in the HTML content
            match = re.search(pattern, html)

            if match:
                # Now, get all items via this weird json structure
                g_rgAssets_str = match.group(1)
                json_items = json.loads(g_rgAssets_str)

                for i in range(1, 3):
                    try:
                        json_items = next(iter(json_items.values()))
                    except:
                        return -1

                return json_items
            else:
                logging.warning("g_rgAssets not found.")
                return None

def get_revenue_price(skin_price):
    # 150% profit for random stickers, 10% for identical stickers
    return [skin_price + (skin_price * 1.5), skin_price + (skin_price * 0.10)]
