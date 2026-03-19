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
    rows: list[RankingRow]
    total_count: int
    returned_count: int

    class Config:
        from_attributes = True
