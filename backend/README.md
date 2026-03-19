# NPB Baseball Statistics API Backend

A production-ready FastAPI backend for managing NPB (Nippon Professional Baseball) statistics. Built with SQLAlchemy ORM, async support, and a clean layered architecture.

## Architecture Overview

The backend follows a clean layered architecture:

- **Routes**: FastAPI endpoint handlers with request validation
- **Services**: Business logic layer for complex operations
- **Repositories**: Data access abstraction layer
- **Models**: SQLAlchemy ORM models representing database entities
- **Schemas**: Pydantic models for request/response validation

## Key Features

### Database Design

The database is designed with a stat-driven model where `stat_definitions` table controls which statistics exist:

- **Adding a new stat** = adding a row to `stat_definitions`, no code changes needed
- All stat columns are nullable (handles incomplete data)
- Supports both SQLite (development) and PostgreSQL (production)
- Full async support via `aiosqlite` for SQLite

### Dynamic Rankings

The Rankings API accepts `stat_key` parameter to sort by any stat dynamically. Automatically handles:
- Sort direction (ascending/descending) from stat definition
- Decimal places for display
- Minimum thresholds (min_pa, min_ip)
- Team/role filtering

### Data Models

#### Teams (12 NPB Teams)
- **Central League**: Giants, Tigers, Carp, Dragons, Swallows, BayStars
- **Pacific League**: Hawks, Eagles, Lions, Marines, Fighters, Buffaloes

#### Players
- NPB ID (unique identifier)
- Full bilingual names (Japanese/English)
- Position, batting/throwing hand, birth date
- Active status tracking

#### Statistics Tables
- `stat_definitions`: Defines all available stats with metadata
- `batter_season_stats`, `pitcher_season_stats`, `team_season_stats`: Full-season stats
- `batter_monthly_stats`, `pitcher_monthly_stats`: Monthly breakdown stats

#### Stat Definition Metadata
Each stat tracks:
- Display names in Japanese and English
- Category (batter/pitcher/team)
- Sort direction (asc/desc)
- Decimal places for display
- Eligibility for rankings/comparisons/graphs
- Whether it's a rate stat vs counting stat

## API Endpoints

### Rankings API
```
GET /api/rankings/batters?season=2024&stat_key=ops&team_code=giants&min_pa=443&limit=20&order=desc
GET /api/rankings/pitchers?season=2024&stat_key=era&role=starter&min_ip=143&limit=20&order=asc
GET /api/rankings/teams?season=2024&stat_key=win_pct&order=desc
```

### Players API
```
GET /api/players/{player_id}
GET /api/players/{player_id}/stats?type=batter
GET /api/players/{player_id}/monthly?season=2024
GET /api/players/search?q=大谷
```

### Comparison API
```
GET /api/compare/players?ids=1,2,3,4&season=2024&type=batter
GET /api/compare/teams?codes=g,t,h,e&season=2024
```

### Teams API
```
GET /api/teams
GET /api/teams/{team_code}/stats?season=2024
```

### Metadata API
```
GET /api/meta/stats?category=batter
GET /api/meta/seasons
GET /api/meta/teams
```

## Setup & Running

### Local Development (SQLite)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Database will automatically initialize at `/app/data/baseball.db` with:
- All tables created
- All stat definitions seeded
- All 12 NPB teams with correct codes and bilingual names

Player and season statistics are not bundled. Populate them by running the scraper in `../scraper`.
The current scraper prefers Baseball Reference and automatically falls back to NPB official pages when Baseball Reference returns 403 or no rows.

### Docker Deployment

```bash
docker build -t baseball-api .
docker run -p 8000:8000 -v $(pwd)/data:/app/data baseball-api
```

### PostgreSQL Migration

Switch to PostgreSQL by setting environment variable:

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost/baseball_db"
```

The code is fully compatible with PostgreSQL without any changes.

## Development

### Adding a New Statistic

1. Add a row to `stat_definitions` table:
```python
StatDefinition(
    stat_key="new_stat",
    display_name_ja="新しい統計",
    display_name_en="New Statistic",
    category="batter",  # or "pitcher" or "team"
    display_order=18,
    decimal_places=3,
    sort_direction="desc",
    is_ranking_eligible=True,
    is_comparable=True,
    is_graphable=True,
    is_rate_stat=True,  # or False for counting stats
    description="Description of the stat"
)
```

2. Add the column to the corresponding stats table (if needed)
3. No code changes required - API will automatically support ranking/comparison

### Adding a New Endpoint

1. Create a new route file in `app/api/routes/`
2. Import and register in `app/api/__init__.py`:
```python
router.include_router(new_route.router)
```

### Project Structure Details

```
app/
├── main.py              # FastAPI app initialization, middleware, health checks
├── config.py            # Configuration from environment variables
├── database.py          # SQLAlchemy setup, migrations, initial master data seeding
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic validation schemas
├── repositories/        # Data access layer
├── services/            # Business logic layer
├── calculators/         # Utility functions for stat calculations
└── api/
    └── routes/          # FastAPI route handlers
```

## Database Schema

All tables include `created_at` and `updated_at` timestamps for auditing.

### stat_definitions
- Drives which stats exist and their properties
- Adding stats doesn't require code changes
- Supports both rate stats (averages, percentages) and counting stats (hits, wins)

### players
- Links to teams via `team_id`
- Includes position, jersey number, bilingual names
- `npb_id` is unique identifier from official NPB data

### batter_season_stats, pitcher_season_stats, team_season_stats
- Full-season aggregate statistics
- All columns nullable (handles incomplete data)
- Indexed by player_id/team_id and season for fast queries

### batter_monthly_stats, pitcher_monthly_stats
- Monthly breakdown for trend analysis
- Same fields as season stats plus month column
- Enables month-by-month comparisons

## Performance Considerations

- Indexes on frequently queried columns (team_code, season, player_id)
- Async database support for non-blocking I/O
- CORS enabled for frontend integration (localhost:3000)
- Efficient repository pattern for data access
- Pagination support in ranking endpoints

## Error Handling

All endpoints include:
- Proper HTTP status codes (404 for not found, 400 for bad requests, 500 for server errors)
- Descriptive error messages
- Input validation via Pydantic schemas

## Dependencies

- **FastAPI 0.104.1**: Modern async web framework
- **SQLAlchemy 2.0**: ORM with async support
- **aiosqlite 0.19**: Async SQLite driver
- **psycopg2-binary 2.9**: PostgreSQL driver (for production)
- **Pydantic 2.5**: Request/response validation
- **uvicorn 0.24**: ASGI server
- **Alembic 1.12**: Database migrations (optional)

## Seeded Master Data

### Stat Definitions
- Batter, pitcher, team statistics metadata used by ranking/comparison APIs

### Teams (12 NPB Teams)
- Official team codes, Japanese names, English names, and league assignment

### Not seeded
- Players
- Batter season stats
- Pitcher season stats
- Team season stats beyond the master rows

These are expected to be imported by the scraper.

## Frontend Integration

The API is fully CORS-enabled for frontend at:
- http://localhost:3000
- http://localhost:3001

The frontend can query any endpoint directly without authentication (development mode).

## Future Enhancements

Planned features:
- Authentication and authorization
- Rate limiting
- Caching layer
- Real-time stat updates via WebSockets
- Database migration support via Alembic
- Advanced filtering and aggregations
- Historical stat comparisons
