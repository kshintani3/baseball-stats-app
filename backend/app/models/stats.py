from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class BatterSeasonStats(BaseModel):
    """Batter season statistics."""

    __tablename__ = "batter_season_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    games = Column(Integer, nullable=True)
    plate_appearances = Column(Integer, nullable=True)
    at_bats = Column(Integer, nullable=True)
    hits = Column(Integer, nullable=True)
    doubles = Column(Integer, nullable=True)
    triples = Column(Integer, nullable=True)
    home_runs = Column(Integer, nullable=True)
    rbi = Column(Integer, nullable=True)
    runs = Column(Integer, nullable=True)
    strikeouts = Column(Integer, nullable=True)
    walks = Column(Integer, nullable=True)
    hit_by_pitch = Column(Integer, nullable=True)
    stolen_bases = Column(Integer, nullable=True)
    batting_average = Column(Float, nullable=True)
    on_base_pct = Column(Float, nullable=True)
    slugging_pct = Column(Float, nullable=True)
    ops = Column(Float, nullable=True)

    player = relationship("Player", back_populates="batter_stats")


class PitcherSeasonStats(BaseModel):
    """Pitcher season statistics."""

    __tablename__ = "pitcher_season_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    games = Column(Integer, nullable=True)
    games_started = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True)
    losses = Column(Integer, nullable=True)
    saves = Column(Integer, nullable=True)
    holds = Column(Integer, nullable=True)
    innings_pitched = Column(Float, nullable=True)
    hits_allowed = Column(Integer, nullable=True)
    home_runs_allowed = Column(Integer, nullable=True)
    strikeouts = Column(Integer, nullable=True)
    walks_allowed = Column(Integer, nullable=True)
    runs_allowed = Column(Integer, nullable=True)
    earned_runs = Column(Integer, nullable=True)
    era = Column(Float, nullable=True)
    whip = Column(Float, nullable=True)

    player = relationship("Player", back_populates="pitcher_stats")


class TeamSeasonStats(BaseModel):
    """Team season statistics."""

    __tablename__ = "team_season_stats"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    games = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True)
    losses = Column(Integer, nullable=True)
    draws = Column(Integer, nullable=True)
    win_pct = Column(Float, nullable=True)
    runs_scored = Column(Integer, nullable=True)
    runs_allowed = Column(Integer, nullable=True)
    home_runs = Column(Integer, nullable=True)
    stolen_bases = Column(Integer, nullable=True)
    team_batting_avg = Column(Float, nullable=True)
    team_era = Column(Float, nullable=True)

    team = relationship("Team", back_populates="season_stats")


class BatterMonthlyStats(BaseModel):
    """Batter monthly statistics."""

    __tablename__ = "batter_monthly_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False)
    games = Column(Integer, nullable=True)
    plate_appearances = Column(Integer, nullable=True)
    at_bats = Column(Integer, nullable=True)
    hits = Column(Integer, nullable=True)
    doubles = Column(Integer, nullable=True)
    triples = Column(Integer, nullable=True)
    home_runs = Column(Integer, nullable=True)
    rbi = Column(Integer, nullable=True)
    runs = Column(Integer, nullable=True)
    strikeouts = Column(Integer, nullable=True)
    walks = Column(Integer, nullable=True)
    hit_by_pitch = Column(Integer, nullable=True)
    stolen_bases = Column(Integer, nullable=True)
    batting_average = Column(Float, nullable=True)
    on_base_pct = Column(Float, nullable=True)
    slugging_pct = Column(Float, nullable=True)
    ops = Column(Float, nullable=True)

    player = relationship("Player", back_populates="batter_monthly")


class PitcherMonthlyStats(BaseModel):
    """Pitcher monthly statistics."""

    __tablename__ = "pitcher_monthly_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False)
    games = Column(Integer, nullable=True)
    games_started = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=True)
    losses = Column(Integer, nullable=True)
    saves = Column(Integer, nullable=True)
    holds = Column(Integer, nullable=True)
    innings_pitched = Column(Float, nullable=True)
    hits_allowed = Column(Integer, nullable=True)
    home_runs_allowed = Column(Integer, nullable=True)
    strikeouts = Column(Integer, nullable=True)
    walks_allowed = Column(Integer, nullable=True)
    runs_allowed = Column(Integer, nullable=True)
    earned_runs = Column(Integer, nullable=True)
    era = Column(Float, nullable=True)
    whip = Column(Float, nullable=True)

    player = relationship("Player", back_populates="pitcher_monthly")
