import json
import re

def get_all_names():
    with open('data/marketplaceids.json', 'r', encoding="utf8") as f:
        names = json.load(f)
        return names['items'].keys()

def get_skin_url(skin_name: str) -> str:
    url = f"https://steamcommunity.com/market/listings/730/{skin_name:}"
    return url

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
                    json_items = next(iter(json_items.values()))

                return json_items
            else:
                print("g_rgAssets not found.")
                return None