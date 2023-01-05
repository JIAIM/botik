import json

from flask import Flask, request
import requests
from dotenv import load_dotenv
import os
from os.path import join, dirname

app = Flask(__name__)

conn = sqlite3.connect('data.db', check_same_thread=False)
sql = conn.cursor()
"""Повертає токен для боту"""
def get_from_env(key):
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    return os.environ.get(key)

league_buttons = ["Ukraine", "England"]
main_menu = ["Show tournament table", "The list of teams", "Show matches", "Show top players"]
current_data = {
    'current_league': None,
    'current_team': None,
    'current_player': None,
    'current_option': None
}

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
    text = request.json["message"]["text"]
    if text == "Ukraine":
        current_data['current_league'] = text
        send_message(chat_id=chat_id, text="nash", buttons=main_menu)
    elif text == "England":
        current_data['current_league'] = text
        send_message(chat_id=chat_id, text="main", buttons=main_menu)
    elif text == "/start":
        send_message(chat_id=chat_id, text=f"Hi {user_name}! Welcome to football bot!\nChoose league:", buttons=league_buttons)
    elif text == "Show tournament table":
        send_message(chat_id=chat_id, text='showing table...')
    elif text == "The list of teams":
        send_message(chat_id=chat_id, text='showing teams...')
    elif text == "Show matches":
        current_data['current_option'] = text
        send_message(chat_id=chat_id, text='Enter the tour between 1:16')

    elif text == "Show top players":
        send_message(chat_id=chat_id, text='showing players...')
    elif current_data['current_option'] == 'Show matches':
        if 0 < int(text) < 17:
             send_message(chat_id=chat_id, text=db.show_mathces(sql.execute("SELECT * from")))
    else:
        send_message(chat_id=chat_id, text=f"Sorry, I can`t understand you, please click on the button", buttons=league_buttons)

    print(request.json)

    return {"ok": True}


if __name__ == '__main__':
    app.run()
