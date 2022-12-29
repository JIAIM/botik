from html.parser import HTMLParser
import json
from abc import ABC
import requests
from bs4 import BeautifulSoup
import re


class IParser(ABC):
    pass


class ITeamsParser(IParser):
    pass


class IGamesParser(IParser):
    pass


class IPlayersParser(IParser):
    pass


class UPLParser:

    def __init__(self, link):
        self.page = self.page_to_html(link)

    def page_to_html(self, link):
        temp_page = requests.get(link)
        return BeautifulSoup(temp_page.content, 'html.parser')


class TeamParser(UPLParser):

    def __init__(self, link):
        super().__init__(link)

    def parse_teams(self):
        result = {
            'teams': []
        }
        team_list = self.page.find('table', class_='main-tournament-table')
        items = team_list.find_all('tr')
        for item in items:
            try:
                team_name = item.find('td', class_='team').find('a').text
                print(team_name)
                num = item.find('td', class_='num').text
                print(num)
                games = item.find('td', class_='games').text
                win = item.find('td', class_='win').text
                draw = item.find('td', class_='draw').text
                lose = item.find('td', class_='lose').text
                goal = item.find('td', class_='goal').text
                miss = item.find('td', class_='miss').text
                diff = item.find('td', class_='diff').text
                score = item.find('td', class_='score').text
                result['teams'].append(
                    {
                    'team_name': team_name,
                    'games': games,
                    'win': win,
                    'draw': draw,
                    'lose': lose,
                    'goal': goal,
                    'miss': miss,
                    'diff': diff,
                    'score': score
                    })


            except AttributeError:
                pass
        return result


class GameParser(UPLParser):

    def __init__(self, link):
        super().__init__(link)

    def parse_games(self):
        result = {
            'games': []
        }
        games_list = self.page.find('div', class_='table-block')
        games = games_list.find_all('div', class_='match')
        for game in games:
            try:
                time = game.find('td', class_='time').find('a').text
                first_team = game.find('td', class_='left-team').find('a').text
                second_team = game.find('td', class_='right-team').find('a').text
                date = game.find_previous('p', class_='match-date').text
                num_of_tour = game.find_previous('div', class_='match-name').find('h4').text
                num_of_tour = re.findall(r'\d+', num_of_tour)[0]
                try:
                    score = game.find('td', class_='score ended').find('a').text
                except AttributeError:
                    score = game.find('td', class_='score').find('a').text

                result['games'].append(
                    {
                    'time': time,
                    'first_team': first_team,
                    'second_team': second_team,
                    'date': date,
                    'num_of_tour': num_of_tour,
                    'score': score
                    })

            except AttributeError:
                pass
        return result


class PlayerParser(UPLParser):

    def __init__(self, link):
        super().__init__(link)

    def parse_player_link(self, link):
        players_links = []
        page = self.page_to_html(link)
        all_links = page.find_all('a', class_='mat-list-team fw-500')
        for one_link in all_links:
            if ('https://www.ua-football.com'+one_link['href']) not in players_links:
                players_links.append('https://www.ua-football.com'+one_link['href'])
        print(players_links)
        with open('players_links.txt', 'a') as file:
            file.write('\n'.join(players_links))
            # for item in players_links:
            #     file.write(item)

        #print('https://www.ua-football.com/ua/'+page.find('a', class_='mat-list-team fw-500')['href'])



    def parse_player(self):
        result = dict()
        keys = ['full_name', 'team_name', 'nationality', 'position', 'age', 'height', 'games_played', 'minutes_played',
                'games_from_start', 'subtitles', 'games_missed', 'goals', 'assists', 'positive_actions', 'yellow_cards',
                'red_cards']
        championship_name = 'Чемпионат Украины'
        try:
            result = {
                'full_name': self.page.find('h1', class_='liga-header__title').text.strip(),
            }
            for i, value in enumerate(
                    self.page.find('div', {'class': 'team-about-header'}).find('div').find_all('alAb-dop-item'), 1
            ):
                result[keys[i]] = value.strip()
            table = self.page.find('table')
            champ_row = None
            for row in table.find('tbody').find_all('tr'):
                if row.find('td').text.strip() == championship_name:
                    champ_row = row
                    break
            if champ_row is None:
                raise ValueError("No value for championhip %s", championship_name)
            for i, value in enumerate(champ_row.find_all('td')[1:], 6):
                result[keys[i]] = value.text.strip()

        except Exception as e:
            raise e
        print(result)

        return result





teams = TeamParser('https://football.ua/ukraine/table.html')
teams_dict= teams.parse_teams()
example1 = GameParser('https://football.ua/ukraine/results/761/')
print(example1.parse_games())
example2 = PlayerParser('https://www.ua-football.com/ua/stats/player/65408-mihail-mudrikua')
example2.parse_player()
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1533-sk-dnipro-1')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/2-shahtar-doneck')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1-dinamo-kiev')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/18-zorya-lugansk')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/5-fk-oleksandriya')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1254-kolos-kovalevka')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1504-metalist-1925-harkov')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/352-krivbas-krivoy-rog')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/4-vorskla-poltava')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1230-veres-rovno')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/6200-metalist-harkov')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1410-ruh-lvov')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1619-fk-minay')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/1253-ingulec-petrovo')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/14-chornomorec-odessa')
example2.parse_player_link('https://www.ua-football.com/ua/stats/team/312-fk-lviv')



