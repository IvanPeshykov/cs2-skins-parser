import logging
import os
import requests
import json
import locale
from dotenv import load_dotenv

# Adaptation of https://github.com/nurettn/Steam-Currency-Converter


steam_currencies = ['A$', 'ARS$', None, 'R$', 'CDN$', 'CHF', 'CLP$', '¥', 'COL$', '₡', '€', '£', 'HK$', '₪', 'Rp', '₹',
                    '¥', '₩', 'KD', '₸', 'Mex$', 'RM', 'kr', 'NZ$', 'S/.', 'P', 'zł', 'QR', 'руб', 'SR', 'S$', '฿',
                    'TL', 'NT$', '₴', '$', '$U', '₫', 'R', 'kr', 'AED']

ISO4217_CurrencyCodes = ['AUD',  'ARS', 'AUD', 'BRL', 'CAD', 'CHF', 'CLP', 'CNY', 'COP', 'CRC', 'EUR', 'GBP', 'HKD',
                         'ILS', 'IDR', 'INR', 'JPY', 'KRW', 'KWD', 'KZT', 'MXN', 'MYR', 'NOK', 'NZD', 'PEN', 'PHP',
                         'PLN', 'QAR', 'RUB', 'SAR', 'SGD', 'THB', 'TRY', 'TWD', 'UAH', 'USD', 'UYU', 'VND', 'ZAR',
                         'SEK', 'AED']

load_dotenv()

currencyJSON = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "currency.json")))

class SteamCurrencyExchanger(object):

    @staticmethod
    def updateCurrencyJSONFile():
        url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"
        response = requests.get(url)
        currencyJSON = response.json()  # Usd based currency
        currencyJSON["usd"] = {key.upper(): value for key, value in currencyJSON["usd"].items()}
        with open(os.path.join(os.path.dirname(__file__), "..", "data", "currency.json"), 'w') as f:
            json.dump(currencyJSON, f, indent=4)

    def convertPrice(self, input_val, autobuy_price, currency_type: str = 'USD') -> float:
        """
        Price converter main function.
        Converts the price to target currency and returns as float.
        """
        currency_type = currency_type.upper()  # Ensure uppercase for currency type
        input_val = self.makeReadable(input_val)

        if input_val == 'Sold!':
            return -1

        foreign_currency = self.getISOCurrencyFromString(input_val)
        actual_price_with_foreign_currency = self.getPriceFromString(input_val, foreign_currency)

        # Validate extracted price
        if actual_price_with_foreign_currency <= 0:
            logging.error(f"Invalid price extracted: {actual_price_with_foreign_currency}")
            return -1

        final_price = self.getEquivalentValue(actual_price_with_foreign_currency, foreign_currency, currency_type)

        # Ensure final price is a valid float
        try:
            final_price = float(locale.format_string("%.2f", final_price, grouping=True))
        except ValueError:
            logging.error(f"Error formatting price: {final_price}")
            return -1

        # Handle special cases for CNY to JPY conversion
        if foreign_currency == 'CNY' and (final_price > autobuy_price + 10 or final_price + 5 < autobuy_price):
            final_price = self.getEquivalentValue(actual_price_with_foreign_currency, 'JPY', currency_type)
            try:
                final_price = float(locale.format_string("%.2f", final_price, grouping=True))
            except ValueError:
                logging.error(f"Error formatting price: {final_price}")
                return -1


        # Sometimes the price is too high or too low, so we return autobuy price, which is not the best solution,
        # but it is better than returning a wrong price.

        if final_price > autobuy_price + 10:
            logging.warning(
                f"There might be an error with the price, it is too high: {final_price}, autobuy: {autobuy_price}")
            logging.info(input_val)
            return autobuy_price

        elif final_price + 5 < autobuy_price:
            logging.warning(
                f"There might be an error with the price, it is too low: {final_price}, autobuy: {autobuy_price}")
            logging.info(input_val)
            return autobuy_price

        return final_price

    def getISOCurrencyFromString(self, s) -> str:
        """Returns the ISO code of the input currency.
        """
        steamCurrency = self.getCurrencySymbolFromString(s)

        # '$2.05 USD' -> '$'.  USD' -> '$'
        if '$' in steamCurrency and 'USD' in steamCurrency:
            steamCurrency = '$'

        iso_equivalent_currency = ISO4217_CurrencyCodes[steam_currencies.index(steamCurrency)]
        return iso_equivalent_currency

    def makeReadable(self, s: str) -> str:
        """Replaces comma with dot and deletes the hypen,
        and strips with the dots.
        """
        s = s.strip()
        s = s.replace(',', '.')
        s = s.replace('-', '')
        s = s.strip('.')
        return s

    def getCurrencySymbolFromString(self, s) -> str:
        """
        Matches and returns the first currency symbol found in the string.
        Checks both prefixes and suffixes.
        """
        for symbol in sorted(steam_currencies, key=lambda x: len(x or ''), reverse=True):
            if symbol and (symbol in s):
                return symbol
        return ''

    def getPriceFromString(self, s, foreign_currency) -> float:
        """
        Extracts and returns float price value.
        Removes spaces, replaces commas with dots,
        and strips out all non-numeric, non-dot characters.
        """
        clean_string = s.replace(' ', '').replace(',', '.')
        number = ''.join((char if char in '0123456789.' else '') for char in clean_string)

        try:
            # Edge case for prices like "100.000.000 IDR" which uses dots as thousands separators
            if ((len(number) > 7 or foreign_currency == 'VND' or foreign_currency == 'CLP'
                 or foreign_currency == 'KRW' or foreign_currency == 'INR')
                    and foreign_currency != 'IDR' and foreign_currency != "KZT"):
                number = number.replace('.', '', 1)
            number = float(number)
        except ValueError as val_err:
            logging.error(f"Value error extracting price: {val_err}, input: {s}")
            number = -1
        except Exception as e:
            logging.error(f"Unexpected error extracting price: {e}, input: {s}")
            number = -1

        return number

    def getEquivalentValue(self, price, steamCurrency, targetCurrency='USD') -> float:
        # Return price as it is if currency types are the same
        if steamCurrency == targetCurrency:
            return price
        # Check if foreignCurrency is base currency type
        if steamCurrency == 'USD':
            baseKatsayi = 1.0
        else:
            baseKatsayi = float(currencyJSON["usd"][steamCurrency])

        # Fetch the base and target coefficients and calculate value
        hedefKatsayi = float(currencyJSON["usd"][targetCurrency])
        convertedPrice = price * hedefKatsayi / baseKatsayi
        return convertedPrice
