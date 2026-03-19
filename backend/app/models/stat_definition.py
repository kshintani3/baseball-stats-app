from sqlalchemy import Column, Integer, String, Boolean, Text, UniqueConstraint
from app.models.base import BaseModel


class StatDefinition(BaseModel):
    """Stat definition model - defines all available statistics."""

    __tablename__ = "stat_definitions"
    __table_args__ = (
        UniqueConstraint("stat_key", "category", name="uq_stat_key_category"),
    )

    id = Column(Integer, primary_key=True, index=True)
    stat_key = Column(String(100), nullable=False, index=True)
    display_name_ja = Column(String(200), nullable=False)
    display_name_en = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    display_order = Column(Integer, nullable=False)
    decimal_places = Column(Integer, default=0)
    sort_direction = Column(String(10), default="desc")
    is_ranking_eligible = Column(Boolean, default=False)
    is_comparable = Column(Boolean, default=True)
    is_graphable = Column(Boolean, default=True)
    is_rate_stat = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
