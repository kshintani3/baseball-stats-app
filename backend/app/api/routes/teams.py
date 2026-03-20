from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.ranking_service import RankingService
from app.services.team_service import TeamService
from app.schemas.ranking import RankingResponse, StandingsResponse
from app.schemas.team import TeamResponse
from app.schemas.stats import TeamSeasonStatsResponse
from typing import Optional, List

router = APIRouter(prefix="", tags=["teams"])


@router.get("/teams", response_model=List[TeamResponse])
async def get_all_teams(
    league: Optional[str] = Query(None, description="Filter by league (central/pacific)"),
    session: AsyncSession = Depends(get_session),
):
    """Get all teams, optionally filtered by league."""
    try:
        service = TeamService(session)
        if league:
            teams = await service.get_teams_by_league(league)
        else:
            teams = await service.get_all_teams()
        return [TeamResponse.model_validate(team) for team in teams]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_code}/stats", response_model=TeamSeasonStatsResponse)
async def get_team_season_stats(
    team_code: str, season: int = Query(...), session: AsyncSession = Depends(get_session)
):
    """Get team season stats."""
    try:
        service = TeamService(session)
        stats = await service.get_team_season_stats(team_code, season)
        if not stats:
            raise HTTPException(status_code=404, detail="Team stats not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/standings", response_model=StandingsResponse)
async def get_standings(
    season: int = Query(..., description="Season year"),
    league: Optional[str] = Query(None, description="Filter by league (central/pacific)"),
    session: AsyncSession = Depends(get_session),
):
    """Get league standings for a season."""
    try:
        service = RankingService(session)
        return await service.get_standings(season=season, league=league)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rankings/teams", response_model=RankingResponse)
async def get_team_rankings(
    season: int = Query(..., description="Season year"),
    stat_key: str = Query(..., description="Stat key for ranking"),
    league: Optional[str] = Query(None, description="Filter by league (central/pacific)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    order: Optional[str] = Query(None, description="Sort order (asc/desc)"),
    session: AsyncSession = Depends(get_session),
):
    """Get team rankings by stat."""
    try:
        service = RankingService(session)
        return await service.get_team_rankings(
            season=season,
            stat_key=stat_key,
            league=league,
            limit=limit,
            order=order,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
