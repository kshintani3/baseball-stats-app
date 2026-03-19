from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.stat_repo import StatRepository
from app.repositories.player_repo import PlayerRepository
from app.repositories.team_repo import TeamRepository
from app.models.stats import BatterSeasonStats, PitcherSeasonStats, TeamSeasonStats
from app.schemas.compare import ComparisonResponse, ComparisonRow
from typing import Optional, List
from app.schemas.stats import (
    BatterSeasonStatsResponse,
    PitcherSeasonStatsResponse,
    TeamSeasonStatsResponse,
)


class CompareService:
    """Service for comparing players and teams."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.stat_repo = StatRepository(session)
        self.player_repo = PlayerRepository(session)
        self.team_repo = TeamRepository(session)

    async def compare_batter_stats(
        self, player_ids: List[int], season: int
    ) -> ComparisonResponse:
        """Compare batter stats for multiple players."""
        players_data = []

        for player_id in player_ids:
            player = await self.player_repo.get_by_id(player_id)
            if not player:
                continue

            stats = await self.stat_repo.get_batter_season_stats(player_id, season)
            if not stats:
                continue

            team = player.team
            stats_dict = {
                "games": stats.games,
                "plate_appearances": stats.plate_appearances,
                "at_bats": stats.at_bats,
                "hits": stats.hits,
                "doubles": stats.doubles,
                "triples": stats.triples,
                "home_runs": stats.home_runs,
                "rbi": stats.rbi,
                "runs": stats.runs,
                "strikeouts": stats.strikeouts,
                "walks": stats.walks,
                "hit_by_pitch": stats.hit_by_pitch,
                "stolen_bases": stats.stolen_bases,
                "batting_average": stats.batting_average,
                "on_base_pct": stats.on_base_pct,
                "slugging_pct": stats.slugging_pct,
                "ops": stats.ops,
            }

            players_data.append(
                ComparisonRow(
                    id=player.id,
                    name_ja=player.name_ja,
                    name_en=player.name_en,
                    team_code=team.code if team else None,
                    team_short_name=team.short_name if team else None,
                    position=player.position,
                    stats=stats_dict,
                )
            )

        stat_keys = [
            "games",
            "plate_appearances",
            "at_bats",
            "hits",
            "doubles",
            "triples",
            "home_runs",
            "rbi",
            "runs",
            "strikeouts",
            "walks",
            "hit_by_pitch",
            "stolen_bases",
            "batting_average",
            "on_base_pct",
            "slugging_pct",
            "ops",
        ]

        return ComparisonResponse(
            category="batter",
            season=season,
            stat_keys=stat_keys,
            rows=players_data,
        )

    async def compare_pitcher_stats(
        self, player_ids: List[int], season: int
    ) -> ComparisonResponse:
        """Compare pitcher stats for multiple players."""
        players_data = []

        for player_id in player_ids:
            player = await self.player_repo.get_by_id(player_id)
            if not player:
                continue

            stats = await self.stat_repo.get_pitcher_season_stats(player_id, season)
            if not stats:
                continue

            team = player.team
            stats_dict = {
                "games": stats.games,
                "games_started": stats.games_started,
                "wins": stats.wins,
                "losses": stats.losses,
                "saves": stats.saves,
                "holds": stats.holds,
                "innings_pitched": stats.innings_pitched,
                "hits_allowed": stats.hits_allowed,
                "home_runs_allowed": stats.home_runs_allowed,
                "strikeouts": stats.strikeouts,
                "walks_allowed": stats.walks_allowed,
                "runs_allowed": stats.runs_allowed,
                "earned_runs": stats.earned_runs,
                "era": stats.era,
                "whip": stats.whip,
            }

            players_data.append(
                ComparisonRow(
                    id=player.id,
                    name_ja=player.name_ja,
                    name_en=player.name_en,
                    team_code=team.code if team else None,
                    team_short_name=team.short_name if team else None,
                    position=player.position,
                    stats=stats_dict,
                )
            )

        stat_keys = [
            "games",
            "games_started",
            "wins",
            "losses",
            "saves",
            "holds",
            "innings_pitched",
            "hits_allowed",
            "home_runs_allowed",
            "strikeouts",
            "walks_allowed",
            "runs_allowed",
            "earned_runs",
            "era",
            "whip",
        ]

        return ComparisonResponse(
            category="pitcher",
            season=season,
            stat_keys=stat_keys,
            rows=players_data,
        )

    async def compare_team_stats(
        self, team_codes: List[str], season: int
    ) -> ComparisonResponse:
        """Compare team stats for multiple teams."""
        teams_data = []

        for team_code in team_codes:
            team = await self.team_repo.get_by_code(team_code)
            if not team:
                continue

            stats = await self.stat_repo.get_team_season_stats(team.id, season)
            if not stats:
                continue

            stats_dict = {
                "games": stats.games,
                "wins": stats.wins,
                "losses": stats.losses,
                "draws": stats.draws,
                "win_pct": stats.win_pct,
                "runs_scored": stats.runs_scored,
                "runs_allowed": stats.runs_allowed,
                "home_runs": stats.home_runs,
                "stolen_bases": stats.stolen_bases,
                "team_batting_avg": stats.team_batting_avg,
                "team_era": stats.team_era,
            }

            teams_data.append(
                ComparisonRow(
                    id=team.id,
                    name_ja=team.name_ja,
                    name_en=team.name_en,
                    team_code=team.code,
                    team_short_name=team.short_name,
                    stats=stats_dict,
                )
            )

        stat_keys = [
            "games",
            "wins",
            "losses",
            "draws",
            "win_pct",
            "runs_scored",
            "runs_allowed",
            "home_runs",
            "stolen_bases",
            "team_batting_avg",
            "team_era",
        ]

        return ComparisonResponse(
            category="team",
            season=season,
            stat_keys=stat_keys,
            rows=teams_data,
        )
