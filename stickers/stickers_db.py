import sqlite3
from datetime import datetime, timedelta

# Class for storing and managing sticker prices in a SQLite database

class StickersDB:

    def __init__(self):
        self.conn = sqlite3.connect('data/stickers.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stickers (
                name TEXT PRIMARY KEY,
                price REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()


    def get_sticker_price(self, name):
        self.cursor.execute('''
            SELECT price, last_updated FROM stickers WHERE name = ?
        ''', (name,))
        result = self.cursor.fetchone()

        if result is None:
            self.remove_sticker(name)
            return None

        # If price was checked more than a week ago, return None
        date_format = "%Y-%m-%d %H:%M:%S"
        converted_datetime = datetime.strptime(result[1], date_format)

        if datetime.now() - converted_datetime > timedelta(weeks=4):
            return None

        return result[0]

    def remove_sticker(self, name):
        self.cursor.execute('''
            DELETE FROM stickers WHERE name = ?
        ''', (name,))
        self.conn.commit()

    def add_sticker(self, name, price):
        self.cursor.execute('''
            INSERT INTO stickers (name, price, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(name) DO UPDATE SET
                price = excluded.price,
                last_updated = CURRENT_TIMESTAMP
        ''', (name, price))
        self.conn.commit()
