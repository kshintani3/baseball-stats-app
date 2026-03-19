from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from app.models.stats import (
    BatterSeasonStats,
    PitcherSeasonStats,
    TeamSeasonStats,
    BatterMonthlyStats,
    PitcherMonthlyStats,
)
from app.models.player import Player
from app.models.team import Team
from app.models.stat_definition import StatDefinition
from typing import Optional, List, Tuple


class StatRepository:
    """Repository for statistics data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_batter_season_stats(
        self, player_id: int, season: int
    ) -> Optional[BatterSeasonStats]:
        """Get batter season stats for a player."""
        query = select(BatterSeasonStats).where(
            and_(
                BatterSeasonStats.player_id == player_id,
                BatterSeasonStats.season == season,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_pitcher_season_stats(
        self, player_id: int, season: int
    ) -> Optional[PitcherSeasonStats]:
        """Get pitcher season stats for a player."""
        query = select(PitcherSeasonStats).where(
            and_(
                PitcherSeasonStats.player_id == player_id,
                PitcherSeasonStats.season == season,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_batter_all_seasons(self, player_id: int) -> List[BatterSeasonStats]:
        """Get all batter season stats for a player."""
        query = (
            select(BatterSeasonStats)
            .where(BatterSeasonStats.player_id == player_id)
            .order_by(BatterSeasonStats.season.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_pitcher_all_seasons(self, player_id: int) -> List[PitcherSeasonStats]:
        """Get all pitcher season stats for a player."""
        query = (
            select(PitcherSeasonStats)
            .where(PitcherSeasonStats.player_id == player_id)
            .order_by(PitcherSeasonStats.season.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_batter_monthly_stats(
        self, player_id: int, season: int
    ) -> List[BatterMonthlyStats]:
        """Get monthly stats for a batter."""
        query = (
            select(BatterMonthlyStats)
            .where(
                and_(
                    BatterMonthlyStats.player_id == player_id,
                    BatterMonthlyStats.season == season,
                )
            )
            .order_by(BatterMonthlyStats.month.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_pitcher_monthly_stats(
        self, player_id: int, season: int
    ) -> List[PitcherMonthlyStats]:
        """Get monthly stats for a pitcher."""
        query = (
            select(PitcherMonthlyStats)
            .where(
                and_(
                    PitcherMonthlyStats.player_id == player_id,
                    PitcherMonthlyStats.season == season,
                )
            )
            .order_by(PitcherMonthlyStats.month.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_team_season_stats(
        self, team_id: int, season: int
    ) -> Optional[TeamSeasonStats]:
        """Get team season stats."""
        query = select(TeamSeasonStats).where(
            and_(
                TeamSeasonStats.team_id == team_id,
                TeamSeasonStats.season == season,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_available_seasons(self) -> List[int]:
        """Get all available seasons across batter, pitcher, and team stats."""
        seasons = set()

        for model in (BatterSeasonStats, PitcherSeasonStats, TeamSeasonStats):
            query = select(model.season.distinct())
            result = await self.session.execute(query)
            seasons.update(season for season in result.scalars().all() if season is not None)

        return sorted(seasons, reverse=True)

    async def get_batter_rankings(
        self,
        season: int,
        stat_key: str,
        team_code: Optional[str] = None,
        min_pa: Optional[int] = None,
        limit: int = 20,
        sort_direction: str = "desc",
    ) -> Tuple[List[Tuple], int]:
        """Get batter rankings."""
        query = (
            select(
                BatterSeasonStats,
                Player,
                Team,
            )
            .join(Player, BatterSeasonStats.player_id == Player.id)
            .join(Team, Player.team_id == Team.id)
            .where(BatterSeasonStats.season == season)
        )

        if team_code:
            query = query.where(Team.code == team_code)

        if min_pa is not None:
            query = query.where(
                or_(
                    BatterSeasonStats.plate_appearances >= min_pa,
                    BatterSeasonStats.plate_appearances.is_(None),
                )
            )

        stat_column = getattr(BatterSeasonStats, stat_key, None)
        if stat_column is not None:
            if sort_direction == "asc":
                query = query.order_by(asc(stat_column))
            else:
                query = query.order_by(desc(stat_column))

        # Count total results before applying limit
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0

        query = query.limit(limit)
        result = await self.session.execute(query)
        rows = result.all()

        return rows, total_count

    async def get_pitcher_rankings(
        self,
        season: int,
        stat_key: str,
        role: Optional[str] = None,
        min_ip: Optional[float] = None,
        limit: int = 20,
        sort_direction: str = "desc",
    ) -> Tuple[List[Tuple], int]:
        """Get pitcher rankings."""
        query = (
            select(
                PitcherSeasonStats,
                Player,
                Team,
            )
            .join(Player, PitcherSeasonStats.player_id == Player.id)
            .join(Team, Player.team_id == Team.id)
            .where(PitcherSeasonStats.season == season)
        )

        if role == "starter":
            query = query.where(
                PitcherSeasonStats.games_started > 0,
            )
        elif role == "reliever":
            query = query.where(
                or_(
                    PitcherSeasonStats.games_started == 0,
                    PitcherSeasonStats.games_started.is_(None),
                )
            )

        if min_ip is not None:
            query = query.where(
                or_(
                    PitcherSeasonStats.innings_pitched >= min_ip,
                    PitcherSeasonStats.innings_pitched.is_(None),
                )
            )

        stat_column = getattr(PitcherSeasonStats, stat_key, None)
        if stat_column is not None:
            if sort_direction == "asc":
                query = query.order_by(asc(stat_column))
            else:
                query = query.order_by(desc(stat_column))

        # Count total results before applying limit
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0

        query = query.limit(limit)
        result = await self.session.execute(query)
        rows = result.all()

        return rows, total_count

    async def get_team_rankings(
        self,
        season: int,
        stat_key: str,
        limit: int = 20,
        sort_direction: str = "desc",
    ) -> Tuple[List[Tuple], int]:
        """Get team rankings."""
        query = (
            select(
                TeamSeasonStats,
                Team,
            )
            .join(Team, TeamSeasonStats.team_id == Team.id)
            .where(TeamSeasonStats.season == season)
        )

        stat_column = getattr(TeamSeasonStats, stat_key, None)
        if stat_column is not None:
            if sort_direction == "asc":
                query = query.order_by(asc(stat_column))
            else:
                query = query.order_by(desc(stat_column))

        # Count total results before applying limit
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0

        query = query.limit(limit)
        result = await self.session.execute(query)
        rows = result.all()

        return rows, total_count
