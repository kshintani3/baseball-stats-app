from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.compare_service import CompareService
from app.schemas.compare import ComparisonResponse
from typing import List

router = APIRouter(prefix="/compare", tags=["compare"])


@router.get("/players", response_model=ComparisonResponse)
async def compare_players(
    ids: str = Query(..., description="Comma-separated player IDs"),
    season: int = Query(...),
    type: str = Query("batter", pattern="^(batter|pitcher)$"),
    session: AsyncSession = Depends(get_session),
):
    """Compare stats for multiple players."""
    try:
        player_ids = [int(pid.strip()) for pid in ids.split(",")]

        service = CompareService(session)

        if type == "batter":
            return await service.compare_batter_stats(player_ids, season)
        else:
            return await service.compare_pitcher_stats(player_ids, season)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams", response_model=ComparisonResponse)
async def compare_teams(
    codes: str = Query(..., description="Comma-separated team codes"),
    season: int = Query(...),
    session: AsyncSession = Depends(get_session),
):
    """Compare stats for multiple teams."""
    try:
        team_codes = [code.strip() for code in codes.split(",")]

        service = CompareService(session)
        return await service.compare_team_stats(team_codes, season)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
