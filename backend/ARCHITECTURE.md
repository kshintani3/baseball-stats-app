# NPB Baseball Statistics API - Architecture Guide

## Overview

This is a production-ready FastAPI backend for NPB (Nippon Professional Baseball) statistics built on modern Python async patterns. The architecture prioritizes maintainability, type safety, and clean separation of concerns.

## Layered Architecture

```
┌─────────────────────────────────────────────────┐
│  FastAPI Routes (api/routes/*.py)              │
│  Request validation & response formatting       │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────▼────────────────────────────┐
│  Business Logic Services (services/*.py)        │
│  Complex operations & data transformations      │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────▼────────────────────────────┐
│  Data Access Repositories (repositories/*.py)   │
│  Database queries & ORM operations              │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────▼────────────────────────────┐
│  SQLAlchemy Models (models/*.py)                │
│  Data entities & database relationships         │
└────────────────────┬────────────────────────────┘
                     │
┌─────────────────────▼────────────────────────────┐
│  SQLite / PostgreSQL Database                   │
│  Persisted statistics & team data              │
└─────────────────────────────────────────────────┘
```

## Directory Structure & Responsibilities

### `/app/main.py`
- FastAPI application initialization
- Middleware setup (CORS)
- Lifespan management (database init/close)
- Health check endpoints
- API documentation setup

### `/app/config.py`
- Environment-based configuration
- Pydantic BaseSettings for validation
- Database URLs, CORS origins, debug flags
- No hardcoded values

### `/app/database.py`
- SQLAlchemy engine creation
- Async session factory
- Database initialization
- Data seeding (stat definitions, NPB teams)
- Dependency injection setup

### `/app/models/` (SQLAlchemy ORM)
- **base.py**: Base model with timestamps
- **team.py**: Team entity (12 NPB teams)
- **player.py**: Player entity with relationships
- **stat_definition.py**: Stat metadata (51 definitions)
- **stats.py**: 5 statistics tables
  - BatterSeasonStats
  - PitcherSeasonStats
  - TeamSeasonStats
  - BatterMonthlyStats
  - PitcherMonthlyStats

### `/app/schemas/` (Pydantic validation)
- Request/response validation
- Type hints for IDE support
- Automatic documentation generation
- Model composition for complex responses
- Bilingual support (JSON serialization)

### `/app/repositories/` (Data Access Layer)
- **player_repo.py**: Player queries (search, get, CRUD)
- **stat_repo.py**: Statistics queries (rankings, seasons)
- **team_repo.py**: Team queries (filtering, selection)
- Database abstraction
- Query optimization
- No business logic here

### `/app/services/` (Business Logic)
- **player_service.py**: Player operations
- **ranking_service.py**: Dynamic rankings (any stat)
- **compare_service.py**: Multi-player/team comparison
- **team_service.py**: Team operations
- Uses repositories for data access
- Transforms data for API responses
- Handles complex calculations

### `/app/calculators/` (Utility functions)
- **stat_calculator.py**: Statistical calculations
- Batting average, OPS, ERA, WHIP, etc.
- Pure functions (no side effects)
- Reusable across services

### `/app/api/routes/` (FastAPI endpoints)
- **batters.py**: `GET /api/rankings/batters`
- **pitchers.py**: `GET /api/rankings/pitchers`
- **teams.py**: `GET /api/teams`, `GET /api/rankings/teams`
- **players.py**: Player detail, search, stats, monthly
- **compare.py**: Player/team comparison
- **meta.py**: Metadata (stats definitions, seasons, teams)
- Request validation via query parameters
- Response formatting via Pydantic schemas
- Error handling with proper HTTP codes

## Data Model Design

### Stat-Driven Architecture (Key Innovation)

The system is driven by the `stat_definitions` table:

```
stat_definitions Table:
┌──────────────────────────────────────────────┐
│ stat_key        │ display_name_ja & en       │
│ category        │ batter/pitcher/team        │
│ sort_direction  │ asc/desc for ranking       │
│ decimal_places  │ 0, 2, or 3                │
│ is_rate_stat    │ boolean                    │
│ is_ranking_eligible │ whether to show in API│
│ is_comparable   │ allow in comparisons       │
│ is_graphable    │ can be visualized          │
└──────────────────────────────────────────────┘
```

Benefits:
- Adding a new stat = 1 database INSERT (no code changes)
- API automatically supports new stats
- Frontend can discover available stats dynamically
- Eliminates hard-coded stat lists

### Foreign Key Relationships

```
teams (1) ────────────────────────── (N) players
                                        │
                                        ├── (N) batter_season_stats
                                        ├── (N) pitcher_season_stats
                                        ├── (N) batter_monthly_stats
                                        └── (N) pitcher_monthly_stats

teams (1) ────────────────────────── (N) team_season_stats
```

All relationships are properly defined with cascades for consistency.

## Async/Await Pattern

All database operations are async:

```python
# Example: Async route with dependency injection
@router.get("/rankings/batters")
async def get_batter_rankings(
    season: int,
    stat_key: str,
    session: AsyncSession = Depends(get_session),  # Injected
) -> RankingResponse:
    service = RankingService(session)
    return await service.get_batter_rankings(season, stat_key)
```

Benefits:
- Non-blocking I/O for database queries
- Handles multiple concurrent requests
- Scales well under load
- Works seamlessly with FastAPI

## Database Compatibility

### SQLite (Default - Development)
```bash
DATABASE_URL=sqlite+aiosqlite:////app/data/baseball.db
```
- File-based, zero setup
- Great for development
- Suitable for small-scale deployments

### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```
- Scalable, concurrent
- Enterprise features
- Just change the URL, code stays the same

## Type Safety

### Route Parameters
```python
@router.get("/rankings/batters")
async def get_batter_rankings(
    season: int = Query(...),           # Type validated
    stat_key: str = Query(...),         # Type validated
    limit: int = Query(20, ge=1, le=100),  # Range validated
    session: AsyncSession = Depends(get_session),
):
```

### Request/Response Models
```python
class RankingResponse(BaseModel):
    stat_key: str                   # Required
    rows: list[RankingRow]          # Type checked
    total_count: int                # Type checked
```

### Database Models
```python
class Team(BaseModel):
    id: int = Column(Integer, primary_key=True)
    code: str = Column(String(10), unique=True)
    league: str = Column(String(20))
```

## Error Handling

Consistent error responses across the API:

```python
# Not found
raise HTTPException(
    status_code=404,
    detail="Player not found"
)

# Bad request
raise HTTPException(
    status_code=400,
    detail="Invalid stat key"
)

# Server error
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=str(e)
    )
```

All errors include proper HTTP status codes and human-readable messages.

## Performance Optimizations

### Database Indexes
- `players.team_id` - for team filtering
- `players.npb_id` - for fast lookups
- `stat tables.player_id, season` - for ranking queries
- `stat tables.season` - for season filtering

### Query Optimization
- Repositories use SQLAlchemy's `.select()` API
- Proper joining to avoid N+1 queries
- Pagination support (limit/offset)
- Filtering before count (where applicable)

### Caching Opportunities
- stat_definitions (rarely changes)
- teams metadata (never changes)
- Previous seasons' stats (read-only)

## Extensibility

### Adding a New Endpoint

1. Create route file: `app/api/routes/new_feature.py`
```python
from fastapi import APIRouter
router = APIRouter(prefix="/api/new", tags=["new"])

@router.get("/data")
async def get_data(session: AsyncSession = Depends(get_session)):
    ...
    return ...
```

2. Register in `app/api/__init__.py`:
```python
from app.api.routes import new_feature
router.include_router(new_feature.router)
```

### Adding a New Statistic

1. Insert into stat_definitions:
```sql
INSERT INTO stat_definitions (
    stat_key, display_name_ja, display_name_en, category,
    display_order, decimal_places, sort_direction, ...
) VALUES (...)
```

2. If needed, add column to stats table:
```python
# In models/stats.py
class BatterSeasonStats(BaseModel):
    new_stat = Column(Float, nullable=True)
```

3. Done! API automatically supports it.

### Adding a New Service

1. Create `app/services/new_service.py`
2. Use repository for data access
3. Use in routes via dependency injection

## Dependency Injection

FastAPI's `Depends()` provides:

```python
# Route gets session automatically
async def get_batter_rankings(
    session: AsyncSession = Depends(get_session)
):
    # Use session
```

Benefits:
- Easy testing (inject mocks)
- Automatic resource cleanup
- Clear dependencies
- Loose coupling

## Bilingual Support

All entities support bilingual names:

```python
class Team(BaseModel):
    name_ja: str  # Japanese name
    name_en: str  # English name
```

```python
class Player(BaseModel):
    name_ja: str
    name_en: str
```

Frontend can:
- Query specific language
- Display both languages
- Select based on user locale

## API Response Format

All responses follow consistent structure:

### Success Response
```json
{
    "stat_key": "ops",
    "stat_name_ja": "OPS",
    "stat_name_en": "OPS",
    "season": 2024,
    "rows": [
        {
            "rank": 1,
            "player_id": 123,
            "name_ja": "大谷翔平",
            "name_en": "Shohei Ohtani",
            "stat_value": 1.234
        }
    ],
    "total_count": 150,
    "returned_count": 20
}
```

### Error Response
```json
{
    "detail": "Invalid stat key 'invalid_stat'"
}
```

## Testing Strategy

The architecture supports easy testing:

### Unit Tests
- Repository layer (mock database)
- Service layer (mock repositories)
- Calculator functions (pure functions)

### Integration Tests
- Routes (use test database)
- End-to-end ranking queries
- Comparison operations

### Mock Injection
```python
def test_ranking_service(session_mock):
    service = RankingService(session_mock)
    result = await service.get_batter_rankings(...)
    assert ...
```

## Deployment

### Docker
```bash
docker build -t baseball-api .
docker run -p 8000:8000 -v data:/app/data baseball-api
```

### Environment Variables
- `DATABASE_URL`: Database connection string
- `DEBUG`: Debug mode (True/False)
- `CORS_ORIGINS`: Comma-separated allowed origins

### Production Checklist
- [ ] Set DATABASE_URL to PostgreSQL
- [ ] Set DEBUG=False
- [ ] Configure CORS_ORIGINS for frontend domain
- [ ] Use gunicorn or similar production ASGI server
- [ ] Set up SSL/TLS
- [ ] Configure logging
- [ ] Set up monitoring/alerting
- [ ] Database backups

## Monitoring & Logging

Current setup includes:
- Health check endpoint (`/health`)
- Error messages with proper HTTP codes
- SQLAlchemy logging (when DEBUG=True)

For production, consider:
- Structured logging (JSON format)
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Database monitoring
- Request tracing

## Conclusion

This backend architecture provides:

✓ Clean separation of concerns  
✓ Type safety throughout  
✓ Async/await for scalability  
✓ Flexible stat-driven design  
✓ Easy to test and maintain  
✓ Production-ready  
✓ Database agnostic (SQLite/PostgreSQL)  
✓ Extensible for future features  

The codebase is ready for immediate use, data import, and scaling.
