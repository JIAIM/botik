from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, validates
from pars import teams_dict, players_dict, games_dict

Base = declarative_base()
engine = create_engine('sqlite:///data.db', echo=True)
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
    # matches_as_right = relationship("Match", back_populates='team_right')
    # matches_as_left = relationship("Match", back_populates='team_left')

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
    match = relationship("Match")
    team_stats = relationship("Team_stats")
    player_stats = relationship("Player_stats")

    def __repr__(self):
        return f"Season: {self.year}"

class Player(Base):
    __tablename__ = "player_table"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    surname = Column("surname", String)
    age = Column("age", Integer)
    team_id = Column(Integer, ForeignKey("team_table.id"))
    team = relationship("Team", back_populates="players")
    nationality = Column("nationality", String)
    height = Column("height", Integer)
    position = Column("position", String)
    player_stats = relationship("Player_stats")

    def __repr__(self):
        return f"Name: {self.name}\nSurname: {self.surname}\nAge: {self.age}\nTeam: {self.team}\n"\
                f"Nationality: {self.nationality}\nHeight: {self.height}\n Position: {self.position}"

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
        return f"Stats: {self.player}\nSeason: {self.season}\nMinutes played: {self.minutes_played}\n"\
                f"Games from start: {self.games_from_start}\nSubtitles: {self.subtitles}\n"\
                f"Games missed: {self.games_missed}\nGoals: {self.goals}\nAssists: {self.assists}\n"\
                f"Positive actions: {self.positive_actions}\nYellow card: {self.yellow_cards}\n"\
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
        return f"Stats: {self.team}\nSeason: {self.season}\nNumber of games: {self.num_of_games}\n"\
                f"Games won: {self.games_won}\nGames lost: {self.games_lost}\n"\
                f"Goal scored: {self.goals_scored}\nGoals lost: {self.goals_lost}\n"\
                f"Goals_difference: {self.goals_difference}\nPoints: {self.points}"\

class Match(Base):
    __tablename__ = "match_table"

    id = Column("id", Integer, primary_key=True)
    left_team_id = Column(Integer, ForeignKey("team_table.id"))
    right_team_id = Column(Integer, ForeignKey("team_table.id"))
    left_team = relationship("Team", foreign_keys=[left_team_id])
    right_team = relationship("Team", foreign_keys=[right_team_id])
    season = Column(Integer, ForeignKey("season_table.id"))
    left_scored = Column("left_scored", Integer)
    right_scored = Column("right_scored", Integer)
    date = Column("date", DATETIME)
    num_of_tour = Column("num_of_tour", Integer)

    def __repr__(self):
        return f"{self.num_of_tour} {self.left_team}\t{self.left_scored}:{self.right_scored}\t{self.right_team}"\
            f"\t{self.date}"

Base.metadata.create_all(engine)

def insert_teams(teams_d, country_name):
    league = session.query(League).filter(League.country == country_name).first()
    if league:
        for i in range(len(teams_d["teams"])):
            session.add(Team(name=teams_d["teams"][i]["team_name"], league=league))
    else:
        raise ValueError("Enter correct country name")

def insert_team_stats(teams_d, season_data):
    season = session.query(Season).filter(Season.year == season_data).first()
    if season:
        for i in range(len(teams_d["teams"])):
            team = session.query(Team).filter(Team.id == i+1).first()
            session.add(Team_stats(team=team, season=season, num_of_games=teams_d["teams"][i]["games"],
                                   games_won=teams_d["teams"][i]["win"],
                                   games_draw=teams_d["teams"][i]["draw"],
                                   games_lost=teams_d["teams"][i]["lose"],
                                   goals_scored=teams_d["teams"][i]["goal"],
                                   goals_lost=teams_d["teams"][i]["miss"],
                                   goals_difference=teams_d["teams"][i]["diff"],
                                   points=teams_d["teams"][i]["score"]))
    else:
        raise ValueError("Enter correct year")




session.commit()

