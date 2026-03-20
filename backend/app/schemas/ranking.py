from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class RankingRow(BaseModel):
    """Single ranking row."""

    rank: int
    player_id: Optional[int] = None
    team_id: Optional[int] = None
    name_ja: str
    name_en: str
    team_code: Optional[str] = None
    team_short_name: Optional[str] = None
    team_league: Optional[str] = None
    stat_value: Optional[float] = None
    position: Optional[str] = None


class RankingResponse(BaseModel):
    """Ranking response with metadata."""

    stat_key: str
    stat_name_ja: str
    stat_name_en: str
    season: int
    category: str
    sort_direction: str
    decimal_places: int
    league: Optional[str] = None
    rows: list[RankingRow]
    total_count: int
    returned_count: int

    class Config:
        from_attributes = True


class StandingsTeamRow(BaseModel):
    """Single team standings row."""

    rank: int
    team_id: int
    team_code: str
    name_ja: str
    name_en: str
    short_name: str
    league: str
    games: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None
    win_pct: Optional[float] = None
    games_behind: Optional[float] = None
    runs_scored: Optional[int] = None
    runs_allowed: Optional[int] = None
    home_runs: Optional[int] = None
    stolen_bases: Optional[int] = None
    team_batting_avg: Optional[float] = None
    team_era: Optional[float] = None


class LeagueStandings(BaseModel):
    """Standings for a single league."""

    league: str
    league_name_ja: str
    season: int
    teams: list[StandingsTeamRow]


class StandingsResponse(BaseModel):
    """Full standings response with both leagues."""

    season: int
    leagues: list[LeagueStandings]
