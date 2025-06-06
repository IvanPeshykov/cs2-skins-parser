import json
import re
import logging
import urllib
from data import config
from urllib.parse import unquote
from bs4 import BeautifulSoup
from steam.steam_currency import SteamCurrencyExchanger

# Exchanger for converting prices to USD.
exchanger = SteamCurrencyExchanger()

# Get all skin names from marketplaceids.json file.
def get_all_names():
    with open('data/marketplaceids.json', 'r', encoding="utf8") as f:
        names = json.load(f)
        return names['items'].keys()

# Create a URL for the skin from its name.
def get_skin_url(skin_name: str) -> str:
    url = "https://steamcommunity.com/market/listings/730/"

    if "|" not in skin_name:
        parts = skin_name.split(' ', 1)
        if len(parts) == 2:
            skin_name = f"{parts[0]} | {parts[1]}"
    else:
        skin_name = " | ".join(part.strip() for part in skin_name.split('|', 1))

    # Mark () and | as safe so they don't get percent-encoded
    return url + urllib.parse.quote(skin_name, safe="|")

# Get price of the skin.
def get_price(html, index, autobuy_price):
    soup = BeautifulSoup(html, 'html.parser')
    prices = soup.find_all("span", class_='market_listing_price_with_fee')
    # We have to convert the price to USD, because steam market prices are in different currencies.
    skin_price = exchanger.convertPrice(prices[index].text, autobuy_price)

    if skin_price == -1:
        return skin_price

    return skin_price


# Get rg_assets from the HTML content. It's a special field in steam market that contains all info about skin.
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
    # 150% profit for random stickers (and + 10$), 10% for identical stickers
    return [skin_price * config.SKIN_PRICE_MULTIPLIER + 10, skin_price * config.CONSISTENT_SKIN_MULTIPLIER]

# Text to send to telegram bot when skin is found
def skin_success_text(skin_url, skin_name, autobuy_price, price, profit, steam_profit, stickers_price, stickers_text, position):
    return f"""
Item: <a href='{skin_url}'>{skin_name}</a>
Autobuy: {round(autobuy_price, 2)}$
Price: {round(price, 2)}$
No fee profit: {round(profit, 2)}$ ({round((profit / price) * 100)}%)
Fee profit: {round(steam_profit, 2)}$ ({round((steam_profit / price) * 100)}%)

Stickers:
{stickers_text}
Stickers total price - {round(stickers_price, 2)}$

Position: {position}
"""

# Calculate profit for the skin based on the fact if the stickers are identical or not.
def calculate_profit(skin_price, sticker_price, consistent_price, is_stickers_identical):
    if is_stickers_identical:
        profit = skin_price + consistent_price / 4
    else:
        profit = skin_price + sticker_price / 10

    return abs(skin_price - profit)

def get_action_url(skin_item, skin_id):
    action_url = skin_item['actions'][0]['link']
    return unquote(action_url.replace('%assetid%', skin_id))