from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from app.models.player import Player
from app.models.team import Team
from typing import Optional, List


class PlayerRepository:
    """Repository for player data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, player_id: int) -> Optional[Player]:
        """Get player by ID with team eagerly loaded."""
        query = select(Player).options(selectinload(Player.team)).where(Player.id == player_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_npb_id(self, npb_id: str) -> Optional[Player]:
        """Get player by NPB ID."""
        query = select(Player).where(Player.npb_id == npb_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def search(
        self, query_str: str, team_code: Optional[str] = None, limit: int = 20
    ) -> List[Player]:
        """Search players by name."""
        query = select(Player).options(selectinload(Player.team)).where(
            or_(
                Player.name_ja.ilike(f"%{query_str}%"),
                Player.name_en.ilike(f"%{query_str}%"),
            )
        )

        if team_code:
            query = query.join(Team).where(Team.code == team_code)

        query = query.limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_team(
        self, team_code: str, is_active: bool = True
    ) -> List[Player]:
        """Get all players from a team."""
        query = (
            select(Player)
            .join(Team)
            .where(and_(Team.code == team_code, Player.is_active == is_active))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, player: Player) -> Player:
        """Create new player."""
        self.session.add(player)
        await self.session.commit()
        await self.session.refresh(player)
        return player

    async def update(self, player_id: int, **kwargs) -> Optional[Player]:
        """Update player."""
        player = await self.get_by_id(player_id)
        if not player:
            return None

        for key, value in kwargs.items():
            if hasattr(player, key) and value is not None:
                setattr(player, key, value)

        await self.session.commit()
        await self.session.refresh(player)
        return player

    async def delete(self, player_id: int) -> bool:
        """Delete player."""
        player = await self.get_by_id(player_id)
        if not player:
            return False

        await self.session.delete(player)
        await self.session.commit()
        return True
