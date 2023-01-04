
from flask import Flask, request
import requests
from dotenv import load_dotenv
import os
from os.path import join, dirname

app = Flask(__name__)

"""Повертає токен для боту"""
def get_from_env(key):
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    return os.environ.get(key)

league_buttons = ["Ukraine", "England"]

def send_message(chat_id, text, buttons=None):
    method = "sendMessage"
    token = get_from_env("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}

    if buttons:
        keyboard = [[{"text": button}] for button in buttons]
        reply_markup = {"keyboard": keyboard}
        data["reply_markup"] = reply_markup

    return requests.post(url, json=data)
@app.route('/', methods=["POST"])  # localhost:5000 -> telegram`s message
def process():
    chat_id = request.json["message"]["chat"]["id"]
    user_name = request.json["message"]["from"]["first_name"]
    send_message(chat_id=chat_id, text=f"Hi {user_name}! Welcome to football bot!\nChoose league:", buttons=league_buttons)
    text = request.json["message"]["text"]
    if text == "Ukraine":
        send_message(chat_id=chat_id, text="nash")
    elif text == "England":
        send_message(chat_id=chat_id, text="ne nash")
    else:
        send_message(chat_id=chat_id, text=f"Hi {user_name}! Welcome to football bot!\nChoose league:", buttons=league_buttons)
    print(request.json)
    return {"ok": True}


if __name__ == '__main__':
    app.run()
