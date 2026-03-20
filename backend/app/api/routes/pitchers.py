from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.ranking_service import RankingService
from app.schemas.ranking import RankingResponse
from typing import Optional

router = APIRouter(prefix="/rankings/pitchers", tags=["rankings"])


@router.get("", response_model=RankingResponse)
async def get_pitcher_rankings(
    season: int = Query(..., description="Season year"),
    stat_key: str = Query(..., description="Stat key for ranking"),
    role: Optional[str] = Query(None, description="Filter by role (starter/reliever)"),
    league: Optional[str] = Query(None, description="Filter by league (central/pacific)"),
    min_ip: Optional[float] = Query(None, description="Minimum innings pitched"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    order: Optional[str] = Query(None, description="Sort order (asc/desc)"),
    session: AsyncSession = Depends(get_session),
):
    """Get pitcher rankings by stat."""
    try:
        service = RankingService(session)
        return await service.get_pitcher_rankings(
            season=season,
            stat_key=stat_key,
            role=role,
            league=league,
            min_ip=min_ip,
            limit=limit,
            order=order,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
