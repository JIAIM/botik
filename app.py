from flask import Flask
from dotenv import load_dotenv
import os
from os.path import join, dirname

app = Flask(__name__)

"""Повертає токен для боту"""
def get_from_env(key):
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    return os.environ.get(key)

token = get_from_env("TELEGRAM_BOT_TOKEN")
@app.route('/')
def hello_world():  # put application's code here
    return token


if __name__ == '__main__':
    app.run()
