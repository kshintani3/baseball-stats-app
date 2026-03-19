from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.team_repo import TeamRepository
from app.repositories.stat_repo import StatRepository
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate
from app.schemas.stats import TeamSeasonStatsResponse
from typing import Optional, List


class TeamService:
    """Service for team operations."""

    def __init__(self, session: AsyncSession):
        self.repo = TeamRepository(session)
        self.stat_repo = StatRepository(session)

    async def get_team(self, team_id: int) -> Optional[Team]:
        """Get team by ID."""
        return await self.repo.get_by_id(team_id)

    async def get_team_by_code(self, code: str) -> Optional[Team]:
        """Get team by code."""
        return await self.repo.get_by_code(code)

    async def get_all_teams(self) -> List[Team]:
        """Get all teams."""
        return await self.repo.get_all()

    async def get_teams_by_league(self, league: str) -> List[Team]:
        """Get teams by league."""
        return await self.repo.get_by_league(league)

    async def create_team(self, team_data: TeamCreate) -> Team:
        """Create a new team."""
        team = Team(**team_data.model_dump())
        return await self.repo.create(team)

    async def update_team(self, team_id: int, team_data: TeamUpdate) -> Optional[Team]:
        """Update a team."""
        update_data = team_data.model_dump(exclude_unset=True)
        return await self.repo.update(team_id, **update_data)

    async def delete_team(self, team_id: int) -> bool:
        """Delete a team."""
        return await self.repo.delete(team_id)

    async def get_team_season_stats(
        self, team_code: str, season: int
    ) -> Optional[TeamSeasonStatsResponse]:
        """Get team season stats."""
        team = await self.repo.get_by_code(team_code)
        if not team:
            return None

        stats = await self.stat_repo.get_team_season_stats(team.id, season)
        if not stats:
            return None

        return TeamSeasonStatsResponse.model_validate(stats)
