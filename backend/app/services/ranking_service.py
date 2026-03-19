from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.stat_repo import StatRepository
from app.models.stat_definition import StatDefinition
from app.models.player import Player
from app.models.team import Team
from app.schemas.ranking import RankingResponse, RankingRow
from typing import Optional


class RankingService:
    """Service for ranking operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = StatRepository(session)

    async def get_stat_definition(
        self, stat_key: str, category: str
    ) -> Optional[StatDefinition]:
        """Get stat definition by key within a category."""
        query = select(StatDefinition).where(
            StatDefinition.stat_key == stat_key,
            StatDefinition.category == category,
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_batter_rankings(
        self,
        season: int,
        stat_key: str,
        team_code: Optional[str] = None,
        min_pa: Optional[int] = None,
        limit: int = 20,
        order: Optional[str] = None,
    ) -> RankingResponse:
        """Get batter rankings."""
        stat_def = await self.get_stat_definition(stat_key, "batter")
        if not stat_def:
            raise ValueError(f"Stat key '{stat_key}' not found")

        sort_direction = order or stat_def.sort_direction

        rows_data, total_count = await self.repo.get_batter_rankings(
            season=season,
            stat_key=stat_key,
            team_code=team_code,
            min_pa=min_pa,
            limit=limit,
            sort_direction=sort_direction,
        )

        ranking_rows = []
        for rank, (stat_row, player, team) in enumerate(rows_data, 1):
            stat_value = getattr(stat_row, stat_key, None)
            ranking_rows.append(
                RankingRow(
                    rank=rank,
                    player_id=player.id,
                    name_ja=player.name_ja,
                    name_en=player.name_en,
                    team_code=team.code,
                    team_short_name=team.short_name,
                    stat_value=stat_value,
                    position=player.position,
                )
            )

        return RankingResponse(
            stat_key=stat_key,
            stat_name_ja=stat_def.display_name_ja,
            stat_name_en=stat_def.display_name_en,
            season=season,
            category=stat_def.category,
            sort_direction=sort_direction,
            decimal_places=stat_def.decimal_places,
            rows=ranking_rows,
            total_count=total_count,
            returned_count=len(ranking_rows),
        )

    async def get_pitcher_rankings(
        self,
        season: int,
        stat_key: str,
        role: Optional[str] = None,
        min_ip: Optional[float] = None,
        limit: int = 20,
        order: Optional[str] = None,
    ) -> RankingResponse:
        """Get pitcher rankings."""
        stat_def = await self.get_stat_definition(stat_key, "pitcher")
        if not stat_def:
            raise ValueError(f"Stat key '{stat_key}' not found")

        sort_direction = order or stat_def.sort_direction

        rows_data, total_count = await self.repo.get_pitcher_rankings(
            season=season,
            stat_key=stat_key,
            role=role,
            min_ip=min_ip,
            limit=limit,
            sort_direction=sort_direction,
        )

        ranking_rows = []
        for rank, (stat_row, player, team) in enumerate(rows_data, 1):
            stat_value = getattr(stat_row, stat_key, None)
            ranking_rows.append(
                RankingRow(
                    rank=rank,
                    player_id=player.id,
                    name_ja=player.name_ja,
                    name_en=player.name_en,
                    team_code=team.code,
                    team_short_name=team.short_name,
                    stat_value=stat_value,
                    position=player.position,
                )
            )

        return RankingResponse(
            stat_key=stat_key,
            stat_name_ja=stat_def.display_name_ja,
            stat_name_en=stat_def.display_name_en,
            season=season,
            category=stat_def.category,
            sort_direction=sort_direction,
            decimal_places=stat_def.decimal_places,
            rows=ranking_rows,
            total_count=total_count,
            returned_count=len(ranking_rows),
        )

    async def get_team_rankings(
        self,
        season: int,
        stat_key: str,
        limit: int = 20,
        order: Optional[str] = None,
    ) -> RankingResponse:
        """Get team rankings."""
        stat_def = await self.get_stat_definition(stat_key, "team")
        if not stat_def:
            raise ValueError(f"Stat key '{stat_key}' not found")

        sort_direction = order or stat_def.sort_direction

        rows_data, total_count = await self.repo.get_team_rankings(
            season=season,
            stat_key=stat_key,
            limit=limit,
            sort_direction=sort_direction,
        )

        ranking_rows = []
        for rank, (stat_row, team) in enumerate(rows_data, 1):
            stat_value = getattr(stat_row, stat_key, None)
            ranking_rows.append(
                RankingRow(
                    rank=rank,
                    team_id=team.id,
                    name_ja=team.name_ja,
                    name_en=team.name_en,
                    team_code=team.code,
                    team_short_name=team.short_name,
                    stat_value=stat_value,
                )
            )

        return RankingResponse(
            stat_key=stat_key,
            stat_name_ja=stat_def.display_name_ja,
            stat_name_en=stat_def.display_name_en,
            season=season,
            category=stat_def.category,
            sort_direction=sort_direction,
            decimal_places=stat_def.decimal_places,
            rows=ranking_rows,
            total_count=total_count,
            returned_count=len(ranking_rows),
        )
