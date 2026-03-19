from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models.stat_definition import StatDefinition
from app.models.team import Team
from app.repositories.stat_repo import StatRepository
from app.repositories.team_repo import TeamRepository
from app.schemas.meta import StatsMetaResponse, StatDefinitionResponse, SeasonsResponse, TeamsMetaResponse
from typing import Optional

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/stats", response_model=StatsMetaResponse)
async def get_stats_meta(
    category: Optional[str] = None, session: AsyncSession = Depends(get_session)
):
    """Get stat definitions metadata."""
    try:
        query = select(StatDefinition)
        if category:
            query = query.where(StatDefinition.category == category)
        query = query.order_by(StatDefinition.display_order.asc())

        result = await session.execute(query)
        stats = result.scalars().all()

        return StatsMetaResponse(
            category=category or "all",
            stats=[StatDefinitionResponse.model_validate(stat) for stat in stats],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/seasons", response_model=SeasonsResponse)
async def get_available_seasons(session: AsyncSession = Depends(get_session)):
    """Get available seasons."""
    try:
        stat_repo = StatRepository(session)
        seasons = await stat_repo.get_available_seasons()
        return SeasonsResponse(seasons=sorted(seasons, reverse=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams", response_model=TeamsMetaResponse)
async def get_teams_meta(session: AsyncSession = Depends(get_session)):
    """Get teams metadata."""
    try:
        team_repo = TeamRepository(session)
        teams = await team_repo.get_all()

        teams_data = [
            {
                "id": team.id,
                "code": team.code,
                "name_ja": team.name_ja,
                "name_en": team.name_en,
                "short_name": team.short_name,
                "league": team.league,
            }
            for team in teams
        ]

        return TeamsMetaResponse(teams=teams_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
