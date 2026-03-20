from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.stat_repo import StatRepository
from app.repositories.team_repo import TeamRepository
from app.models.stat_definition import StatDefinition
from app.models.player import Player
from app.models.team import Team
from app.models.stats import TeamSeasonStats
from app.schemas.ranking import (
    RankingResponse,
    RankingRow,
    StandingsResponse,
    LeagueStandings,
    StandingsTeamRow,
)
from typing import Optional


LEAGUE_NAMES_JA = {
    "central": "セントラル・リーグ",
    "pacific": "パシフィック・リーグ",
}


class RankingService:
    """Service for ranking operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = StatRepository(session)
        self.team_repo = TeamRepository(session)

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
        league: Optional[str] = None,
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
            league=league,
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
                    team_league=team.league,
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
            league=league,
            rows=ranking_rows,
            total_count=total_count,
            returned_count=len(ranking_rows),
        )

    async def get_pitcher_rankings(
        self,
        season: int,
        stat_key: str,
        role: Optional[str] = None,
        league: Optional[str] = None,
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
            league=league,
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
                    team_league=team.league,
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
            league=league,
            rows=ranking_rows,
            total_count=total_count,
            returned_count=len(ranking_rows),
        )

    async def get_team_rankings(
        self,
        season: int,
        stat_key: str,
        league: Optional[str] = None,
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
            league=league,
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
                    team_league=team.league,
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
            league=league,
            rows=ranking_rows,
            total_count=total_count,
            returned_count=len(ranking_rows),
        )

    async def get_standings(
        self,
        season: int,
        league: Optional[str] = None,
    ) -> StandingsResponse:
        """Get league standings for a season."""
        leagues_to_fetch = [league] if league else ["central", "pacific"]
        league_standings = []

        for lg in leagues_to_fetch:
            teams = await self.team_repo.get_by_league(lg)
            team_rows = []

            for team in teams:
                stats = await self.repo.get_team_season_stats(team.id, season)
                team_rows.append(
                    StandingsTeamRow(
                        rank=0,  # Will be set after sorting
                        team_id=team.id,
                        team_code=team.code,
                        name_ja=team.name_ja,
                        name_en=team.name_en,
                        short_name=team.short_name,
                        league=team.league,
                        games=stats.games if stats else None,
                        wins=stats.wins if stats else None,
                        losses=stats.losses if stats else None,
                        draws=stats.draws if stats else None,
                        win_pct=stats.win_pct if stats else None,
                        games_behind=None,
                        runs_scored=stats.runs_scored if stats else None,
                        runs_allowed=stats.runs_allowed if stats else None,
                        home_runs=stats.home_runs if stats else None,
                        stolen_bases=stats.stolen_bases if stats else None,
                        team_batting_avg=stats.team_batting_avg if stats else None,
                        team_era=stats.team_era if stats else None,
                    )
                )

            # Sort by win_pct descending (teams without stats go to bottom)
            team_rows.sort(
                key=lambda t: (t.win_pct is not None, t.win_pct or 0),
                reverse=True,
            )

            # Calculate rank and games behind
            leader_win_pct = None
            leader_wins = 0
            leader_losses = 0
            for i, row in enumerate(team_rows):
                row.rank = i + 1
                if i == 0 and row.win_pct is not None:
                    leader_win_pct = row.win_pct
                    leader_wins = row.wins or 0
                    leader_losses = row.losses or 0
                    row.games_behind = 0.0
                elif leader_win_pct is not None and row.wins is not None and row.losses is not None:
                    # Games behind = ((leader_wins - team_wins) + (team_losses - leader_losses)) / 2
                    gb = ((leader_wins - (row.wins or 0)) + ((row.losses or 0) - leader_losses)) / 2
                    row.games_behind = gb

            league_standings.append(
                LeagueStandings(
                    league=lg,
                    league_name_ja=LEAGUE_NAMES_JA.get(lg, lg),
                    season=season,
                    teams=team_rows,
                )
            )

        return StandingsResponse(
            season=season,
            leagues=league_standings,
        )
