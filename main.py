import os
import smtplib
import sqlite3
import ssl
import time

import requests
import selectorlib

URL = "http://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


class Event:
    @staticmethod
    def scrape(url):
        """Scrape the page source from the URL"""
        response = requests.get(url, headers=HEADERS)
        source = response.text
        return source

    @staticmethod
    def extract(source):
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)["tours"]
        return value


class Email:
    @staticmethod
    def send(message):
        host = "smtp.gmail.com"
        port = 465

        password = os.getenv("GMAIL_PASSWORD")
        username = os.getenv("SENDER")
        receiver = os.getenv("RECEIVER")

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, message)
        print("Email was sent!")


class Database:
    def __init__(self, database_path):
        self.connection = sqlite3.connect(database_path)

    def store(self, _extracted):
        _row = _extracted.split(",")
        _row = [item.strip() for item in _row]
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", _row)
        self.connection.commit()

    def read(self, _extracted):
        _row = _extracted.split(",")
        _row = [item.strip() for item in _row]
        band, city, date = _row
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
        rows = cursor.fetchall()
        print(rows)
        return rows


if __name__ == "__main__":
    while True:
        event = Event()
        scraped = event.scrape(URL)
        extracted = event.extract(scraped)

        print(extracted)

        if extracted != "No upcoming tours":
            database = Database(database_path="data.db")
            row = database.read(extracted)
            if not row:
                database.store(extracted)
                email = Email()
                email.send(message="Hey, new event was found!")
        time.sleep(2)
