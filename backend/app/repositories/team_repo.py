from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.team import Team
from typing import Optional, List


class TeamRepository:
    """Repository for team data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, team_id: int) -> Optional[Team]:
        """Get team by ID."""
        query = select(Team).where(Team.id == team_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_code(self, code: str) -> Optional[Team]:
        """Get team by code."""
        query = select(Team).where(Team.code == code)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self) -> List[Team]:
        """Get all teams."""
        query = select(Team).order_by(Team.league.asc(), Team.short_name.asc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_league(self, league: str) -> List[Team]:
        """Get teams by league."""
        query = select(Team).where(Team.league == league).order_by(Team.short_name.asc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, team: Team) -> Team:
        """Create new team."""
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        return team

    async def update(self, team_id: int, **kwargs) -> Optional[Team]:
        """Update team."""
        team = await self.get_by_id(team_id)
        if not team:
            return None

        for key, value in kwargs.items():
            if hasattr(team, key) and value is not None:
                setattr(team, key, value)

        await self.session.commit()
        await self.session.refresh(team)
        return team

    async def delete(self, team_id: int) -> bool:
        """Delete team."""
        team = await self.get_by_id(team_id)
        if not team:
            return False

        await self.session.delete(team)
        await self.session.commit()
        return True
