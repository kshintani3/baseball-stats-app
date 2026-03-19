from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StatDefinitionResponse(BaseModel):
    """Stat definition response."""

    id: int
    stat_key: str
    display_name_ja: str
    display_name_en: str
    category: str
    display_order: int
    decimal_places: int
    sort_direction: str
    is_ranking_eligible: bool
    is_comparable: bool
    is_graphable: bool
    is_rate_stat: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StatsMetaResponse(BaseModel):
    """Stats metadata response."""

    category: str
    stats: list[StatDefinitionResponse]


class SeasonsResponse(BaseModel):
    """Available seasons response."""

    seasons: list[int]


class TeamsMetaResponse(BaseModel):
    """Teams metadata response."""

    teams: list[dict]
