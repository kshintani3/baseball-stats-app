from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TeamBase(BaseModel):
    """Base team schema."""

    code: str
    name_ja: str
    name_en: str
    short_name: str
    league: str


class TeamCreate(TeamBase):
    """Create team schema."""

    pass


class TeamUpdate(BaseModel):
    """Update team schema."""

    name_ja: Optional[str] = None
    name_en: Optional[str] = None
    short_name: Optional[str] = None
    league: Optional[str] = None


class TeamResponse(TeamBase):
    """Team response schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
