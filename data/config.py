# Use this file to configure the bot's settings

# Enable or disable the use of proxies.
USE_PROXY = True
# Enable or disable full traceback logging.
DEBUG = False
# Amount of threads to use for parsing.
THREADS_NUM = 10
# Prices

# Multiplier for skins without consistent stickers. So, for example, if multiplier is 1.5, in order to match,
# stickers price should be 150% of skin price
SKIN_PRICE_MULTIPLIER = 1.5
# The same but for skins with consistent stickers.
CONSISTENT_SKIN_MULTIPLIER = 1.1

# Sleep time between each skin parsing.
SKIN_SLEEP_TIME_MIN = 30
SKIN_SLEEP_TIME_MAX = 40

# Cooldown for proxy that is being rate limited.
TOO_MANY_REQUESTS_COOLDOWN = 10

# Sleep time between each sticker parsing.
STICKER_SLEEP_TIME = 1

# This is the settings for filtering skins, that will appear in wrong.txt file.
MIN_PRICE = 0.5
MAX_PRICE = 50
MIN_SELL_AMOUNT = 0
