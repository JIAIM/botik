from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///data.db', echo=True)
# Base.metadata.create_all(engine)

class League(Base):
    __tablename__ = "league_table"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    country = Column("country", String)
    teams = relationship("Team")

    def __repr__(self):
        return f"League: {self.name}\t Country: {self.country}"


class Team(Base):
    __tablename__ = "team_table"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    league = Column(Integer, ForeignKey("league_table.id"))
    team_stats = relationship("Team_stat")
    left_team = relationship("Match")
    right_team = relationship("Match")
    player = relationship("Player")

    def __repr__(self):
        return f"Name: {self.name}\t Leagues: {self.league}"

class Season(Base):
    __tablename__ = "season_table"

    id = Column("id", Integer, primary_key=True)
    year = Column("year", Integer)
    match = relationship("Match")
    team_stat = relationship("Team_stat")
    player_stat = relationship("Player_stat")

    def __repr__(self):
        return f"Season: {self.year}"

class Player(Base):
    __tablename__ = "player_table"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    surname = Column("surname", String)
    age = Column("age", Integer)
    team = Column(Integer, ForeignKey("team_table.id"))
    nationality = Column("nationality", String)
    height = Column("height", Integer)
    position = Column("position", String)
    player_stats = relationship("Player_stat")


    def __repr__(self):
        return f"Name: {self.name}\nSurname: {self.surname}\nAge: {self.age}\nTeam: {self.team}\n"\
                f"Nationality: {self.nationality}\nHeight: {self.height}\n Position: {self.position}"

class Player_stat(Base):
    __tablename__ = "player_stats_table"

    id = Column("id", Integer, primary_key=True)
    player = Column(Integer, ForeignKey("player_table.id"))
    season = Column(Integer, ForeignKey("season_table.id"))
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

class Team_stat(Base):
    __tablename__ = "team_stats_table"

    id = Column("id", Integer, primary_key=True)
    team = Column(Integer, ForeignKey("team_table.id"))
    season = Column(Integer, ForeignKey("season_table.id"))
    num_of_games = Column("num_of_games", Integer)
    games_won = Column("games_won", Integer)
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
    left_team = Column(Integer, ForeignKey("team_table.id"))
    right_team = Column(Integer, ForeignKey("team_table.id"))
    season = Column(Integer, ForeignKey("season_table.id"))
    left_scored = Column("left_scored", Integer)
    right_scored = Column("right_scored", Integer)
    date = Column("date", DATETIME)
    num_of_tour = Column("num_of_tour", Integer)

    def __repr__(self):
        return f"{self.num_of_tour} {self.left_team}\t{self.left_scored}:{self.right_scored}\t{self.right_team}"\
            f"\t{self.date}"

Base.metadata.create_all(engine)