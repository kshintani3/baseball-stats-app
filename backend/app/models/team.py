from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Team(BaseModel):
    """Team model."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name_ja = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    short_name = Column(String(50), nullable=False)
    league = Column(String(20), nullable=False, index=True)

    players = relationship("Player", back_populates="team")
    season_stats = relationship("TeamSeasonStats", back_populates="team")
