from bs4 import BeautifulSoup
import re
import json

def parse_title(title):
    return "Sticker |" + title.split('Sticker:')[1]

def get_titles(sticker):
    soup = BeautifulSoup(sticker, 'html.parser')
    sticker_div = soup.find(id='sticker_info')
    titles = [parse_title(img['title']) for img in sticker_div.find_all('img')]
    return titles

def get_sticker_url(title):
    url = f"https://steamcommunity.com/market/listings/730/{title}"
    return url

def find_price(html):
    match = re.search('var line1\s*=\s*(\[\[.*?\]\]);', html)

    if match:
        line1_data = match.group(1)
        try:
            # Ensure all elements are JSON-safe
            data = json.loads(line1_data.replace("'", '"'))
            # Get price
            return data[-1][1]
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
            return -1
    else:
        print("g_rgAssets not found.")
        return -1
