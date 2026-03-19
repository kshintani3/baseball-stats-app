from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BatterSeasonStatsBase(BaseModel):
    """Base batter season stats schema."""

    season: int
    games: Optional[int] = None
    plate_appearances: Optional[int] = None
    at_bats: Optional[int] = None
    hits: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    home_runs: Optional[int] = None
    rbi: Optional[int] = None
    runs: Optional[int] = None
    strikeouts: Optional[int] = None
    walks: Optional[int] = None
    hit_by_pitch: Optional[int] = None
    stolen_bases: Optional[int] = None
    batting_average: Optional[float] = None
    on_base_pct: Optional[float] = None
    slugging_pct: Optional[float] = None
    ops: Optional[float] = None


class BatterSeasonStatsResponse(BatterSeasonStatsBase):
    """Batter season stats response."""

    id: int
    player_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PitcherSeasonStatsBase(BaseModel):
    """Base pitcher season stats schema."""

    season: int
    games: Optional[int] = None
    games_started: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    saves: Optional[int] = None
    holds: Optional[int] = None
    innings_pitched: Optional[float] = None
    hits_allowed: Optional[int] = None
    home_runs_allowed: Optional[int] = None
    strikeouts: Optional[int] = None
    walks_allowed: Optional[int] = None
    runs_allowed: Optional[int] = None
    earned_runs: Optional[int] = None
    era: Optional[float] = None
    whip: Optional[float] = None


class PitcherSeasonStatsResponse(PitcherSeasonStatsBase):
    """Pitcher season stats response."""

    id: int
    player_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamSeasonStatsBase(BaseModel):
    """Base team season stats schema."""

    season: int
    games: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None
    win_pct: Optional[float] = None
    runs_scored: Optional[int] = None
    runs_allowed: Optional[int] = None
    home_runs: Optional[int] = None
    stolen_bases: Optional[int] = None
    team_batting_avg: Optional[float] = None
    team_era: Optional[float] = None


class TeamSeasonStatsResponse(TeamSeasonStatsBase):
    """Team season stats response."""

    id: int
    team_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BatterMonthlyStatsBase(BaseModel):
    """Base batter monthly stats schema."""

    season: int
    month: int
    games: Optional[int] = None
    plate_appearances: Optional[int] = None
    at_bats: Optional[int] = None
    hits: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    home_runs: Optional[int] = None
    rbi: Optional[int] = None
    runs: Optional[int] = None
    strikeouts: Optional[int] = None
    walks: Optional[int] = None
    hit_by_pitch: Optional[int] = None
    stolen_bases: Optional[int] = None
    batting_average: Optional[float] = None
    on_base_pct: Optional[float] = None
    slugging_pct: Optional[float] = None
    ops: Optional[float] = None


class BatterMonthlyStatsResponse(BatterMonthlyStatsBase):
    """Batter monthly stats response."""

    id: int
    player_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PitcherMonthlyStatsBase(BaseModel):
    """Base pitcher monthly stats schema."""

    season: int
    month: int
    games: Optional[int] = None
    games_started: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    saves: Optional[int] = None
    holds: Optional[int] = None
    innings_pitched: Optional[float] = None
    hits_allowed: Optional[int] = None
    home_runs_allowed: Optional[int] = None
    strikeouts: Optional[int] = None
    walks_allowed: Optional[int] = None
    runs_allowed: Optional[int] = None
    earned_runs: Optional[int] = None
    era: Optional[float] = None
    whip: Optional[float] = None


class PitcherMonthlyStatsResponse(PitcherMonthlyStatsBase):
    """Pitcher monthly stats response."""

    id: int
    player_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
