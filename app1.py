import telebot
from telebot import types
from dotenv import load_dotenv
import os
from os.path import join, dirname

import db


def get_from_env(key):
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    return os.environ.get(key)


bot = telebot.TeleBot(get_from_env('TELEGRAM_BOT_TOKEN'))

current_data = {'current_option': None,
                'previous_option': None}


@bot.message_handler(commands=["start"])
def start(message):
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    league_option1 = types.KeyboardButton("Українська Прем'єр Ліга")
    league_option2 = types.KeyboardButton('Premiere League')

    start_markup.add(league_option1, league_option2)

    bot.send_message(message.chat.id, 'Choose the league:'.format(message.from_user), reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    menu_option1 = None
    menu_option2 = None
    menu_option3 = None
    menu_option4 = None
    menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == "Українська Прем'єр Ліга":
        menu_option1 = types.KeyboardButton("Турнірна таблиця")
        menu_option2 = types.KeyboardButton("Список команд")
        menu_option3 = types.KeyboardButton("Матчі")
        menu_option4 = types.KeyboardButton("Топ гравців")
        menu_option5 = types.KeyboardButton("До вибору ліги")
        menu_markup.add(menu_option1, menu_option2, menu_option3, menu_option4, menu_option5)
        bot.send_message(message.chat.id, 'Choose the option:'.format(message.from_user), reply_markup=menu_markup)
    elif message.text == "Premiere League":
        menu_option1 = types.KeyboardButton("Tournament table")
        menu_option2 = types.KeyboardButton("List of teams")
        menu_option3 = types.KeyboardButton("Matches")
        menu_option4 = types.KeyboardButton("Top players")
        menu_option5 = types.KeyboardButton("Back to leagues")
        menu_markup.add(menu_option1, menu_option2, menu_option3, menu_option4, menu_option5)
        bot.send_message(message.chat.id, 'Choose the option:'.format(message.from_user), reply_markup=menu_markup)
    elif message.text == "Back to leagues" or message.text == "До вибору ліги":
        start(message)
    elif message.text == "Матчі":
        current_data['current_option'] = message.text
        bot.send_message(message.chat.id, 'Введіть номер туру від 1 до 16')
    elif message.text == "Турнірна таблиця":
        bot.send_message(message.chat.id, db.show_tables())
    elif message.text == "Список команд":
        bot.send_message(message.chat.id, db.show_teams())
        current_data['current_option'] = message.text
        bot.send_message(message.chat.id, "Введіть номер команди для більш детальної інформації")

    elif message.text == "Матчі команди" and isinstance(current_data['current_option'], int):
        bot.send_message(message.chat.id, db.show_team_matches(current_data['current_option']))
    elif message.text == "Гравці" and isinstance(current_data['current_option'], int):
        bot.send_message(message.chat.id, db.show_team_players(current_data['current_option']))
        players_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        players_option1 = types.KeyboardButton('Детальна Інформація')
        players_option2 = types.KeyboardButton('Назад')
        players_markup.add(players_option1, players_option2)
        bot.send_message(message.chat.id, 'Choose the option:'.format(message.from_user), reply_markup=players_markup)
    elif message.text == 'Детальна Інформація':
        current_data['previous_option'] = current_data['current_option'] #team
        current_data['current_option'] = message.text #deteails
        bot.send_message(message.chat.id, 'Ведіть номер гравця:')
    elif current_data['current_option'] == 'Детальна Інформація' and message.text.isnumeric():
        try:
            back_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back_option = types.KeyboardButton('Назад')
            back_markup.add(back_option)
            bot.send_message(message.chat.id, db.show_team_player(current_data['previous_option'], int(message.text)), reply_markup=back_markup)


        except Exception as e:
            bot.send_message(message.chat.id, 'Такого гравця не існує:')
    elif message.text == "Назад" and current_data['current_option'] == 'Детальна Інформація':
        teams_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        teams1 = types.KeyboardButton("Матчі команди")
        teams2 = types.KeyboardButton("Гравці")
        teams3 = types.KeyboardButton("Назад")
        teams_markup.add(teams1, teams2, teams3)
        current_data['current_option'] = current_data['previous_option']
        bot.send_message(message.chat.id, 'Choose the option', reply_markup=teams_markup)


    elif message.text == "Назад" and isinstance(current_data['current_option'], int):
        menu_option1 = types.KeyboardButton("Турнірна таблиця")
        menu_option2 = types.KeyboardButton("Список команд")
        menu_option3 = types.KeyboardButton("Матчі")
        menu_option4 = types.KeyboardButton("Топ гравців")
        menu_option5 = types.KeyboardButton("До вибору ліги")
        menu_markup.add(menu_option1, menu_option2, menu_option3, menu_option4, menu_option5)
        bot.send_message(message.chat.id, 'Choose the option:'.format(message.from_user), reply_markup=menu_markup)
        current_data['current_option'] = "Українська Прем'єр Ліга"
    elif current_data['current_option'] == "Список команд":
        teams_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        teams1 = types.KeyboardButton("Матчі команди")
        teams2 = types.KeyboardButton("Гравці")
        teams3 = types.KeyboardButton("Назад")
        teams_markup.add(teams1, teams2, teams3)
        try:
            if message.text.isnumeric() and 1<=int(message.text)<=16:
                current_data['current_option'] = int(message.text)
                bot.send_message(message.chat.id, 'Оберіть:'.format(message.from_user), reply_markup=teams_markup)
            else:
                bot.send_message(message.chat.id, '!Введіть номер команди від 1 до 16!')
        except ValueError:
            bot.send_message(message.chat.id, '!Введіть номер команди від 1 до 16!')


    elif message.text == "Топ гравців":
        current_data['current_option'] = message.text
        top_players_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        top_players1 = types.KeyboardButton("Лідери по голам")
        top_players2 = types.KeyboardButton("Лідери по асистам")
        top_players3 = types.KeyboardButton("Лідери по жовтим карткам")
        top_players4 = types.KeyboardButton("Лідери по червоним карткам")
        top_players5 = types.KeyboardButton("Назад")
        top_players_markup.add(top_players1, top_players2, top_players3, top_players4, top_players5)
        bot.send_message(message.chat.id, 'Оберіть:'.format(message.from_user), reply_markup=top_players_markup)
        pass
    elif current_data['current_option'] == "Топ гравців":
        if message.text == "Лідери по голам":
            bot.send_message(message.chat.id, db.top_goal_players())
        if message.text == "Лідери по асистам":
            bot.send_message(message.chat.id, db.top_assist_players())
        if message.text == "Лідери по жовтим карткам":
            bot.send_message(message.chat.id, db.top_yellow_players())
        if message.text == "Лідери по червоним карткам":
            bot.send_message(message.chat.id, db.top_red_players())
        if message.text == "Назад":
            menu_option1 = types.KeyboardButton("Турнірна таблиця")
            menu_option2 = types.KeyboardButton("Список команд")
            menu_option3 = types.KeyboardButton("Матчі")
            menu_option4 = types.KeyboardButton("Топ гравців")
            menu_option5 = types.KeyboardButton("До вибору ліги")
            menu_markup.add(menu_option1, menu_option2, menu_option3, menu_option4, menu_option5)
            bot.send_message(message.chat.id, 'Назад. Choose the option:'.format(message.from_user),
                             reply_markup=menu_markup)


    elif current_data['current_option'] == "Матчі":
        if message.text.isnumeric() and 0 < int(message.text) < 17:
            bot.send_message(message.chat.id, db.show_mathces(int(message.text)))
        else:
            bot.send_message(message.chat.id, '!Введіть номер туру від 1 до 16!')

    else:
        bot.send_message(message.chat.id, "Sorry I can`t understand you("
                                          "\nChoose the option or enter correct data")



bot.polling(none_stop=True)
