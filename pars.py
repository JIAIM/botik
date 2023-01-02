from html.parser import HTMLParser
import json
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import re
import os


class IParser(ABC):

    @abstractmethod
    def page_to_html(self, link):
        pass


class ITeamsParser(IParser):

    @abstractmethod
    def parse_teams(self):
        pass


class IGamesParser(IParser):
    @abstractmethod
    def parse_games(self):
        pass


class IPlayersParser(IParser):

    @abstractmethod
    def parse_players(self):
        pass


class IParseFactory(ABC):

    @abstractmethod
    def parse_teams(self):
        pass

    @abstractmethod
    def parse_games(self):
        pass

    @abstractmethod
    def parse_players(self):
        pass


class UPL_Parser(IParser):

    def __init__(self, link):
        self.page = self.page_to_html(link)

    def page_to_html(self, link):
        try:
            return BeautifulSoup(requests.get(link).content, 'html.parser')
        except Exception as e:
            print(e)


class UPL_TeamParser(ITeamsParser, UPL_Parser):

    def __init__(self, link):
        super().__init__(link)

    def parse_teams(self):
        result = {
            'teams': []
        }
        # team_list = self.page.find('table', class_='main-tournament-table')
        # items = team_list.find_all('tr')
        keys = ['num', 'games', 'win', 'draw', 'lose', 'goal', 'miss', 'diff', 'score']
        for item in self.page.find('table', class_='main-tournament-table').find_all('tr'):
            try:
                temp_dict = {i: item.find('td', class_=i).text for i in keys}
                temp_dict['team_name'] = item.find('td', class_='team').find('a').text,
                result['teams'].append(temp_dict)
            except AttributeError:
                pass
        return result


class UPL_GameParser(IGamesParser, UPL_Parser):

    def __init__(self, link):
        super().__init__(link)

    def parse_games(self):
        result = {
            'games': []
        }
        for game in self.page.find('div', class_='table-block').find_all('div', class_='match'):
            try:
                try:
                    score = game.find('td', class_='score ended').find('a').text
                except AttributeError:
                    score = game.find('td', class_='score').find('a').text

                result['games'].append(
                    {
                        'time': game.find('td', class_='time').find('a').text,
                        'first_team': game.find('td', class_='left-team').find('a').text,
                        'second_team': game.find('td', class_='right-team').find('a').text,
                        'date': game.find_previous('p', class_='match-date').text,
                        'num_of_tour': game.find_previous('div', class_='match-name').find('h4').text,
                        'score': score
                    })

            except AttributeError:
                pass
        return result


class UPL_PlayerParser(IPlayersParser, UPL_Parser):

    def __init__(self, squad_file, players_links_file):
        super().__init__(None)
        self.squad_file = squad_file
        self.players_links_file = players_links_file

    def parse_player_link(self):  #
        players_links = []
        with open(self.squad_file, 'r') as f:
            for line in f:
                # players_links = []
                page = self.page_to_html(line)
                for one_link in page.find_all('a', class_='mat-list-team fw-500'):
                    if ('https://www.ua-football.com' + one_link['href']) not in players_links:
                        players_links.append('https://www.ua-football.com' + one_link['href'])
                print(players_links)
        with open(self.players_links_file, 'w') as file:
            # file.write('\n')
            file.write('\n'.join(players_links))

    def parse_single_player(self, page):

        result = dict()
        keys = ['full_name', 'team_name', 'nationality', 'position', 'age', 'height', 'games_played', 'minutes_played',
                'games_from_start', 'subtitles', 'games_missed', 'goals', 'assists', 'positive_actions', 'yellow_cards',
                'red_cards']
        championship_name = 'Общие показатели'
        try:
            result = {
                'full_name': page.find('h1', class_='liga-header__title').text.strip(),
            }
            for i, value in enumerate(
                    page.find('div', {'class': 'team-about-header'}).find_all('div', class_='alAb-dop-n1'), 1
            ):
                result[keys[i]] = value.text.strip()
            table = page.find('table')
            champ_row = None
            for row in table.find('tbody').find_all('tr'):
                if row.find('td').text.strip() == championship_name:
                    champ_row = row
                    break
            if champ_row is None:
                raise ValueError("No value for championhip %s", championship_name)
            for i, value in enumerate(champ_row.find_all('td')[1:], 6):
                result[keys[i]] = value.text.strip()
            result['goals'] = result['goals'][:result['goals'].index(' ')]
            result['age'] = result['age'][:result['age'].index(' ')]
            if result['age'] == '53': result['age'] = None

        except Exception as e:
            raise e
        print(result)

        return result

    def parse_players(self):
        result = []
        self.parse_player_link()
        with open(self.players_links_file, 'r') as f:
            for line in f:
                result.append(self.parse_single_player(self.page_to_html(line)))
        return result


class UPLParseFactory(IParseFactory):

    def __init__(self, teams_link, games_link, squad_file, players_links_file):
        self.teams_link = teams_link
        self.games_link = games_link
        self.squad_file = squad_file
        self.players_links_file = players_links_file

    @property
    def teams_link(self):
        return self.__teams_link

    @teams_link.setter
    def teams_link(self, link):
        if isinstance(link, str) and 'https://' in link:
            self.__teams_link = link

    @property
    def games_link(self):
        return self.__games_link

    @games_link.setter
    def games_link(self, link):
        if isinstance(link, str) and 'https://' in link:
            self.__games_link = link

    @property
    def squad_file(self):
        return self.__squad_file

    @squad_file.setter
    def squad_file(self, squad_file):
        if not os.path.isfile(squad_file):
            raise FileExistsError
        self.__squad_file = squad_file

    @property
    def players_links_file(self):
        return self.__players_links_file

    @players_links_file.setter
    def players_links_file(self, players_links_file):
        if not os.path.isfile(players_links_file):
            raise FileExistsError
        self.__players_links_file = players_links_file

    def parse_games(self):
        return UPL_GameParser(self.games_link).parse_games()

    def parse_teams(self):
        return UPL_TeamParser(self.teams_link).parse_teams()

    def parse_players(self):
        return UPL_PlayerParser(self.squad_file, self.players_links_file).parse_players()


teams_links = 'https://football.ua/ukraine/table.html'
games_link = 'https://football.ua/ukraine/results/761/'
upl = UPLParseFactory(teams_links, games_link, 'upl_squads.txt', 'players_links.txt')
teams_dict = upl.parse_teams()
games_dict = upl.parse_games()
players_dict = upl.parse_players()
