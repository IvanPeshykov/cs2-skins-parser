from bs4 import BeautifulSoup

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

