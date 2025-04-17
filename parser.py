from abc import ABC, abstractmethod
import json
import re
import logging

# Base abstract class for parsers

class Parser(ABC):

    @abstractmethod
    def parse(self):
        pass

    def get_item_price(self, html):
        match = re.search('var line1\s*=\s*(\[\[.*?\]\]);', html)

        if match:
            line1_data = match.group(1)
            try:
                # Ensure all elements are JSON-safe
                data = json.loads(line1_data.replace("'", '"'))
                # Get price
                return data[-1][1]
            except json.JSONDecodeError as e:
                logging.error("Failed to parse JSON:", e)
                return -1
        else:
            logging.warning("Iterm price not found." + html)
            return -1