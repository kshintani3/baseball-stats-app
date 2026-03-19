from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Player(BaseModel):
    """Player model."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    npb_id = Column(String(50), unique=True, nullable=False, index=True)
    name_ja = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    position = Column(String(20), nullable=True)
    bats = Column(String(1), nullable=True)
    throws = Column(String(1), nullable=True)
    birth_date = Column(Date, nullable=True)
    jersey_number = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    team = relationship("Team", back_populates="players")
    batter_stats = relationship("BatterSeasonStats", back_populates="player")
    pitcher_stats = relationship("PitcherSeasonStats", back_populates="player")
    batter_monthly = relationship("BatterMonthlyStats", back_populates="player")
    pitcher_monthly = relationship("PitcherMonthlyStats", back_populates="player")
