from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class PlayerBase(BaseModel):
    """Base player schema."""

    npb_id: str
    name_ja: str
    name_en: str
    position: Optional[str] = None
    bats: Optional[str] = None
    throws: Optional[str] = None
    birth_date: Optional[date] = None
    jersey_number: Optional[int] = None
    is_active: bool = True


class PlayerCreate(PlayerBase):
    """Create player schema."""

    team_id: int


class PlayerUpdate(BaseModel):
    """Update player schema."""

    name_ja: Optional[str] = None
    name_en: Optional[str] = None
    position: Optional[str] = None
    bats: Optional[str] = None
    throws: Optional[str] = None
    birth_date: Optional[date] = None
    jersey_number: Optional[int] = None
    is_active: Optional[bool] = None
    team_id: Optional[int] = None


class PlayerResponse(PlayerBase):
    """Player response schema."""

    id: int
    team_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerDetailResponse(PlayerResponse):
    """Player detail response with team information."""

    team: "TeamResponse" = None


from app.schemas.team import TeamResponse

PlayerDetailResponse.model_rebuild()
