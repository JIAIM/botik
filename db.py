from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, validates
from pars import UPLParseFactory
from sqlalchemy import select
from tabulate import tabulate
import json


Base = declarative_base()
engine = create_engine('sqlite:///data.db?check_same_thread=False', echo=True)
Session = sessionmaker(engine)
session = Session()


class League(Base):
    __tablename__ = "league_table"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    country = Column("country", String)
    teams = relationship("Team")

    @validates('name', 'country')
    def validate_name_and_country(self, _, address):
        if not isinstance(address, str):
            raise TypeError()
        return address

    def __repr__(self):
        return f"League: {self.name}\t Country: {self.country}"


class Team(Base):
    __tablename__ = "team_table"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    league_id = Column(Integer, ForeignKey("league_table.id"))
    league = relationship("League", back_populates="teams")
    team_stats = relationship("Team_stats")
    players = relationship("Player")

    # matches_as_right = relationship("Match", back_populates='right_team')
    # matches_as_left = relationship("Match", back_populates='left_team')

    @validates('name')
    def validate_name(self, _, address):
        if not isinstance(address, str):
            raise TypeError()
        return address

    def __repr__(self):
        return f"Name: {self.name}\t Leagues: {self.league}"


class Season(Base):
    __tablename__ = "season_table"

    id = Column("id", Integer, primary_key=True)
    year = Column("year", Integer)
    matches = relationship("Match")
    team_stats = relationship("Team_stats")
    player_stats = relationship("Player_stats")

    def __repr__(self):
        return f"{self.year}"


class Player(Base):
    __tablename__ = "player_table"

    id = Column("id", Integer, primary_key=True)
    full_name = Column("full_name", String)
    age = Column("age", Integer)
    team_id = Column(Integer, ForeignKey("team_table.id"))
    team = relationship("Team", back_populates="players")
    nationality = Column("nationality", String)
    height = Column("height", Integer)
    position = Column("position", String)
    player_stats = relationship("Player_stats")

    def __repr__(self):
        return f"Full name: {self.full_name}\nAge: {self.age}\nTeam: {self.team}\n" \
               f"Nationality: {self.nationality}\nHeight: {self.height}\nPosition: {self.position}"


class Player_stats(Base):
    __tablename__ = "player_stats_table"

    id = Column("id", Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player_table.id"))
    player = relationship("Player", back_populates="player_stats")
    season_id = Column(Integer, ForeignKey("season_table.id"))
    season = relationship("Season", back_populates="player_stats")
    minutes_played = Column("minutes_played", Integer)
    games_from_start = Column("games_from_start", Integer)
    subtitles = Column("subtitles", Integer)
    games_missed = Column("games_missed", Integer)
    goals = Column("goals", Integer)
    assists = Column("assists", Integer)
    positive_actions = Column("positive_actions", Integer)
    yellow_cards = Column("yellow_cards", Integer)
    red_cards = Column("red_cards", Integer)

    def __repr__(self):
        return f"{self.player}\nSeason: {self.season}\nMinutes played: {self.minutes_played}\n" \
               f"Games from start: {self.games_from_start}\nSubtitles: {self.subtitles}\n" \
               f"Games missed: {self.games_missed}\nGoals: {self.goals}\nAssists: {self.assists}\n" \
               f"Positive actions: {self.positive_actions}\nYellow card: {self.yellow_cards}\n" \
               f"Red card: {self.red_cards}"


class Team_stats(Base):
    __tablename__ = "team_stats_table"

    id = Column("id", Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("team_table.id"))
    team = relationship("Team", back_populates="team_stats")
    season_id = Column(Integer, ForeignKey("season_table.id"))
    season = relationship("Season", back_populates="team_stats")
    num_of_games = Column("num_of_games", Integer)
    games_won = Column("games_won", Integer)
    games_draw = Column("games_draw", Integer)
    games_lost = Column("games_lost", Integer)
    goals_scored = Column("goals_scored", Integer)
    goals_lost = Column("goals_lost", Integer)
    goals_difference = Column("goals_difference", Integer)
    points = Column("points", Integer)

    def __repr__(self):
        return f"{self.team}\nSeason: {self.season}\nNumber of games: {self.num_of_games}\n" \
               f"Games won: {self.games_won}\nGames lost: {self.games_lost}\n" \
               f"Goal scored: {self.goals_scored}\nGoals lost: {self.goals_lost}\n" \
               f"Goals_difference: {self.goals_difference}\nPoints: {self.points}"


class Match(Base):
    __tablename__ = "match_table"

    id = Column("id", Integer, primary_key=True)
    left_team_id = Column(Integer, ForeignKey("team_table.id"))
    right_team_id = Column(Integer, ForeignKey("team_table.id"))
    season_id = Column(Integer, ForeignKey("season_table.id"))
    left_team = relationship("Team", foreign_keys=[left_team_id])
    right_team = relationship("Team", foreign_keys=[right_team_id])
    season = relationship("Season", back_populates="matches")
    left_scored = Column(Integer, nullable=True)
    right_scored = Column(Integer, nullable=True)
    time = Column(String)
    date = Column(String)
    num_of_tour = Column(Integer)

    def __repr__(self):
        return f"?????? - {self.num_of_tour} {self.left_team.name}\t{self.left_scored}:{self.right_scored}\t{self.right_team.name}" \
               f"\t{self.time} {self.date}"


Base.metadata.create_all(engine)


def check_season(season_data):
    result = session.query(Season).filter(Season.year == season_data).first()
    return result


def insert_teams(teams_d, country_name):
    league = session.query(League).filter(League.country == country_name).first()
    if league:
        for i in range(len(teams_d["teams"])):
            session.add(Team(name=str(teams_d["teams"][i]["team_name"])[2:-3], league=league))
    else:
        raise ValueError("Enter correct country name")


def insert_team_stats(teams_d, season_data):
    season = check_season(season_data)
    if season:
        for i in range(len(teams_d["teams"])):
            team = session.query(Team).filter(Team.name == str(teams_d["teams"][i]["team_name"])[2:-3]).first()
            session.add(Team_stats(team=team,
                                   season=season,
                                   num_of_games=teams_d["teams"][i]["games"],
                                   games_won=teams_d["teams"][i]["win"],
                                   games_draw=teams_d["teams"][i]["draw"],
                                   games_lost=teams_d["teams"][i]["lose"],
                                   goals_scored=teams_d["teams"][i]["goal"],
                                   goals_lost=teams_d["teams"][i]["miss"],
                                   goals_difference=teams_d["teams"][i]["diff"],
                                   points=teams_d["teams"][i]["score"]))
    else:
        raise ValueError("Enter correct year")


def insert_player(players_d):
    teams_names_short = ["??????", "??????", "??????", "??????", "??????", "??????", "??????", "1925", "??????", "??????", "??????",
                         "??????", "??????", "??????", "??????", "??????"]
    teams_name = []
    name_to_find = None
    for index in range(16):
        team_correct = str(session.query(Team.name).filter(Team.id == index + 1).first())
        teams_name.append(team_correct[2:-3])

    for i in range(len(players_d)):
        for k in range(16):
            name_to_find = players_d[i]["team_name"]
            if name_to_find.find(teams_names_short[k]) != -1:
                name_to_find = teams_name[k]
                break

        team = session.query(Team).filter(Team.name == name_to_find).first()
        player_data = Player(full_name=players_d[i]["full_name"],
                             age=players_d[i]["age"],
                             team=team,
                             nationality=players_d[i]["nationality"],
                             height=players_d[i]["height"],
                             position=players_d[i]["position"])
        session.add(player_data)


def insert_player_stats(players_d, season_data):
    season = check_season(season_data)
    if season:
        for i in range(len(players_d)):
            player = session.query(Player).filter(Player.full_name == players_d[i]["full_name"]).first()
            session.add(Player_stats(player=player,
                                     season=season,
                                     minutes_played=players_d[i]["minutes_played"],
                                     games_from_start=players_d[i]["games_from_start"],
                                     subtitles=players_d[i]["subtitles"],
                                     games_missed=players_d[i]["games_missed"],
                                     goals=players_d[i]["goals"],
                                     assists=players_d[i]["assists"],
                                     positive_actions=players_d[i]["positive_actions"],
                                     yellow_cards=players_d[i]["yellow_cards"],
                                     red_cards=players_d[i]["red_cards"]))
    else:
        raise ValueError()


def insert_matches(matches_dict, season_data):
    season = check_season(season_data)
    if season:
        for i in range(len(matches_dict["games"])):
            left_team = session.query(Team).filter(Team.name == matches_dict["games"][i]["first_team"]).first()
            right_team = session.query(Team).filter(Team.name == matches_dict["games"][i]["second_team"]).first()
            match = Match(left_team=left_team,
                          right_team=right_team,
                          season=season,
                          left_scored=matches_dict["games"][i]["left_team_score"],
                          right_scored=matches_dict["games"][i]["right_team_score"],
                          time=matches_dict["games"][i]["time"],
                          date=matches_dict["games"][i]["date"],
                          num_of_tour=matches_dict["games"][i]["num_of_tour"])
            session.add(match)
    else:
        raise ValueError()


def show_team_player(team, player_num):
    res_str = ""
    players = session.query(Player).filter(Player.team_id == team)
    play = players[player_num-1]
    play_stat = session.query(Player_stats).filter(Player_stats.player == play).first()
    res_str += str(play_stat)
    return res_str

def show_team_players(team):
    res_str = ""
    i = 1
    players = session.query(Player).filter(Player.team_id == team)
    for player in players:
        if i<10:
            res_str += str(i) +".  "+str(player.full_name) + "\n"
        else:
            res_str += str(i) + ". " + str(player.full_name) + "\n"
        i+=1
    return res_str

def show_team_matches(team_name):
    res_str = ""
    mat = {}
    matches_left = session.query(Match).where(Match.left_team_id == team_name)
    matches_right = session.query(Match).where(Match.right_team_id == team_name)
    for match1 in matches_left:
        id = int(str(match1)[6:8])
        mat[id] = str(match1)
    for match2 in matches_right:
        id = int(str(match2)[6:8])
        mat[id] = str(match2)
    for i in range(len(mat)):
        res_str += mat[i+1] + "\n"
    return res_str

def show_mathces(tour):
    res_str = ''
    stmt = select(Match).where(Match.num_of_tour == tour)
    for match in session.scalars(stmt):
        res_str += str(match) + "\n"
    return res_str

def top_goal_players():
    res_str = ""
    stmt = session.query(Player_stats).order_by(Player_stats.goals).all()
    print(stmt)
    for i in range(1, 6):
        res_str += f"{str(i)}. {str(stmt[-i].player.full_name)} {str(stmt[-i].goals)} {str(stmt[-i].player.team.name)}\n"
    return res_str

def top_assist_players():
    res_str = ""
    stmt = session.query(Player_stats).order_by(Player_stats.assists).all()
    for i in range(1, 6):
        res_str += f"{str(i)}. {str(stmt[-i].player.full_name)} {str(stmt[-i].assists)} {str(stmt[-i].player.team.name)}\n"
    return res_str

def top_red_players():
    res_str = ""
    stmt = session.query(Player_stats).order_by(Player_stats.red_cards).all()
    for i in range(1, 6):
        res_str += f"{i}. {stmt[-i].player.full_name} {stmt[-i].red_cards} \n"
    return res_str

def show_players_of_team(team):
    res_str = ""
    stmt = select(Player).where(Player.team.name == team)
    for i in stmt:
        res_str += i
    return res_str




def top_yellow_players():
    res_str = ""
    stmt = session.query(Player_stats).order_by(Player_stats.yellow_cards).all()
    for i in range(1, 6):
        res_str += f"{str(i)}. {str(stmt[-i].player.full_name)} {str(stmt[-i].yellow_cards)} \n"
    return res_str

def show_teams():
    res_str = ""
    stmt = session.query(Team).order_by(Team.id).all()
    for i in range(16):
        if i<10:
            res_str += f" {str(i+1)}. {str(stmt[i].name)}\n"
        else:
            res_str += f"{str(i+1)}. {str(stmt[i].name)}\n"
    return res_str

def show_tables():
    stms = session.query(Team_stats).order_by(Team_stats.points).all()
    table = [["#","Name","Game","Win","Draw","Lose","GS","GL","GD","Point"]]
    for i in range(1, 17):
            temp = []
            temp.append(str(i))
            temp.append(str(stms[-i].team.name))
            temp.append(str(stms[-i].num_of_games))
            temp.append(str(stms[-i].games_won))
            temp.append(str(stms[-i].games_draw))
            temp.append(str(stms[-i].games_lost))
            temp.append(str(stms[-i].goals_scored))
            temp.append(str(stms[-i].goals_lost))
            temp.append(str(stms[-i].goals_difference))
            temp.append(str(stms[-i].points))
            table.append(temp)
    return tabulate(table, headers='firstrow')

def update_data():
    teams_links = 'https://football.ua/ukraine/table.html'
    games_link = 'https://football.ua/ukraine/results/761/'
    upl = UPLParseFactory(teams_links, games_link, 'upl_squads.txt', 'players_links.txt')
    teams_dict = upl.parse_teams()
    games_dict = upl.parse_games()
    players_list = upl.parse_players()
    session.add(League(name="Ukrainian Premier League", country="Ukraine"))
    session.add(Season(year=2022))
    insert_teams(teams_dict, "Ukraine")
    insert_team_stats(teams_dict, 2022)
    insert_player(players_list)
    insert_player_stats(players_list, 2022)
    insert_matches(games_dict, 2022)
    session.commit()


session.commit()
