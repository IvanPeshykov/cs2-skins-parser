

class StickersParser:

    def __init__(self, skin_item):
        self.skin_item = skin_item
        self.stickers = self.find_stickers(skin_item)

    @staticmethod
    def is_valid(skin_item):
        return len(skin_item['descriptions']) >= 7 and StickersParser.find_stickers(skin_item) is not None

    @staticmethod
    def find_stickers(skin_item):

        for description in skin_item['descriptions']:
            if description['name'] == 'sticker_info':
                return description

        return None

    def parse(self):
        print(self.stickers)

