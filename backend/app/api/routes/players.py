from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.player_service import PlayerService
from app.schemas.player import PlayerResponse, PlayerDetailResponse
from app.schemas.stats import BatterSeasonStatsResponse, PitcherSeasonStatsResponse, BatterMonthlyStatsResponse, PitcherMonthlyStatsResponse
from app.repositories.stat_repo import StatRepository
from typing import Optional, List

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/search", response_model=List[PlayerResponse])
async def search_players(
    q: str = Query(..., description="Search query"),
    team_code: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """Search players by name."""
    try:
        service = PlayerService(session)
        players = await service.search_players(q, team_code, limit)
        return [PlayerResponse.model_validate(player) for player in players]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}", response_model=PlayerDetailResponse)
async def get_player(player_id: int, session: AsyncSession = Depends(get_session)):
    """Get player by ID."""
    try:
        service = PlayerService(session)
        player = await service.get_player(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return PlayerDetailResponse.model_validate(player)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}/stats", response_model=List[BatterSeasonStatsResponse] | List[PitcherSeasonStatsResponse])
async def get_player_stats(
    player_id: int,
    type: str = Query("batter", pattern="^(batter|pitcher)$"),
    session: AsyncSession = Depends(get_session),
):
    """Get all season stats for a player."""
    try:
        service = PlayerService(session)
        player = await service.get_player(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        stat_repo = StatRepository(session)

        if type == "batter":
            stats = await stat_repo.get_batter_all_seasons(player_id)
            return [BatterSeasonStatsResponse.model_validate(stat) for stat in stats]
        else:
            stats = await stat_repo.get_pitcher_all_seasons(player_id)
            return [PitcherSeasonStatsResponse.model_validate(stat) for stat in stats]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}/monthly", response_model=List[BatterMonthlyStatsResponse] | List[PitcherMonthlyStatsResponse])
async def get_player_monthly_stats(
    player_id: int,
    season: int = Query(...),
    type: str = Query("batter", pattern="^(batter|pitcher)$"),
    session: AsyncSession = Depends(get_session),
):
    """Get monthly stats for a player."""
    try:
        service = PlayerService(session)
        player = await service.get_player(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        stat_repo = StatRepository(session)

        if type == "batter":
            stats = await stat_repo.get_batter_monthly_stats(player_id, season)
            return [BatterMonthlyStatsResponse.model_validate(stat) for stat in stats]
        else:
            stats = await stat_repo.get_pitcher_monthly_stats(player_id, season)
            return [PitcherMonthlyStatsResponse.model_validate(stat) for stat in stats]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
