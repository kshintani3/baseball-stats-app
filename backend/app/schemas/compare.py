from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComparisonRow(BaseModel):
    """Single player/team comparison row."""

    id: int
    name_ja: str
    name_en: str
    team_code: Optional[str] = None
    team_short_name: Optional[str] = None
    position: Optional[str] = None
    stats: dict[str, Optional[float]]

    class Config:
        from_attributes = True


class ComparisonResponse(BaseModel):
    """Comparison response."""

    category: str
    season: int
    stat_keys: list[str]
    rows: list[ComparisonRow]

    class Config:
        from_attributes = True
