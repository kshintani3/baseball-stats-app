from fastapi import APIRouter
from app.api.routes import batters, pitchers, teams, players, rankings, compare, meta

router = APIRouter()

router.include_router(batters.router)
router.include_router(pitchers.router)
router.include_router(teams.router)
router.include_router(players.router)
router.include_router(rankings.router)
router.include_router(compare.router)
router.include_router(meta.router)

__all__ = ["router"]
