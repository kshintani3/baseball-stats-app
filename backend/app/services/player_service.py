from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.player_repo import PlayerRepository
from app.models.player import Player
from app.schemas.player import PlayerCreate, PlayerUpdate
from typing import Optional, List


class PlayerService:
    """Service for player operations."""

    def __init__(self, session: AsyncSession):
        self.repo = PlayerRepository(session)

    async def get_player(self, player_id: int) -> Optional[Player]:
        """Get player by ID."""
        return await self.repo.get_by_id(player_id)

    async def get_player_by_npb_id(self, npb_id: str) -> Optional[Player]:
        """Get player by NPB ID."""
        return await self.repo.get_by_npb_id(npb_id)

    async def search_players(
        self, query: str, team_code: Optional[str] = None, limit: int = 20
    ) -> List[Player]:
        """Search players by name."""
        return await self.repo.search(query, team_code, limit)

    async def get_team_players(
        self, team_code: str, is_active: bool = True
    ) -> List[Player]:
        """Get all players from a team."""
        return await self.repo.get_by_team(team_code, is_active)

    async def create_player(self, player_data: PlayerCreate) -> Player:
        """Create a new player."""
        player = Player(**player_data.model_dump())
        return await self.repo.create(player)

    async def update_player(
        self, player_id: int, player_data: PlayerUpdate
    ) -> Optional[Player]:
        """Update a player."""
        update_data = player_data.model_dump(exclude_unset=True)
        return await self.repo.update(player_id, **update_data)

    async def delete_player(self, player_id: int) -> bool:
        """Delete a player."""
        return await self.repo.delete(player_id)
