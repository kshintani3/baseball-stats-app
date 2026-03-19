# Quick Start Guide

## 1. Install Dependencies

```bash
cd /sessions/confident-sweet-edison/mnt/cowork/baseball-app/backend
pip install -r requirements.txt
```

## 2. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will:
- Start on http://localhost:8000
- Automatically create the SQLite database
- Initialize all tables and stat definitions
- Seed all 12 NPB teams as master data

## 3. Verify Installation

Visit in your browser:
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- http://localhost:8000/redoc - Alternative API documentation (ReDoc)
- http://localhost:8000/health - Health check endpoint

## 4. Test Endpoints

### Get all teams metadata:
```bash
curl http://localhost:8000/api/meta/teams
```

### Get available seasons:
```bash
curl http://localhost:8000/api/meta/seasons
```

### Get batter stat definitions:
```bash
curl http://localhost:8000/api/meta/stats?category=batter
```

## 5. Load Real Data

The backend bootstraps table definitions and team/stat metadata, but it does not include player or season statistics.

Populate the database from the scraper before using ranking endpoints:

```bash
cd ../scraper
pip install -r requirements.txt
python cli.py fetch --year 2024 --type teams
python cli.py fetch --year 2024 --type batters
python cli.py fetch --year 2024 --type pitchers
```

The scraper tries Baseball Reference first and automatically falls back to NPB official pages if Baseball Reference returns 403 or no rows.
If you only load `teams`, metadata and team rankings will work, but batter/pitcher rankings will stay empty.

## 6. Database Location

SQLite database is created at:
```
/app/data/baseball.db
```

To reset the database, delete this file and rerun the scraper.

## 7. Switch to PostgreSQL (Optional)

Set environment variable before running:
```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/baseball_db"
```

Or add to `.env` file:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/baseball_db
```

## 8. Docker Deployment

```bash
docker build -t baseball-api .
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DATABASE_URL="sqlite+aiosqlite:////app/data/baseball.db" \
  baseball-api
```

## API Usage Examples

### Get batter rankings by OPS:
```bash
curl "http://localhost:8000/api/rankings/batters?season=2024&stat_key=ops&limit=10&min_pa=300"
```

### Search players:
```bash
curl "http://localhost:8000/api/players/search?q=%E5%A4%A7%E8%B0%B7"  # 大谷 in URL encoding
```

### Compare players:
```bash
curl "http://localhost:8000/api/compare/players?ids=1,2,3&season=2024&type=batter"
```

### Get team stats:
```bash
curl "http://localhost:8000/api/teams/g/stats?season=2024"  # Giants (g)
```

## Database Schema

The database includes:
- `teams` - All 12 NPB teams
- `players` - Player information (will be populated by your data import)
- `stat_definitions` - Definitions for all 51+ statistics
- `batter_season_stats` - Batter full-season statistics
- `pitcher_season_stats` - Pitcher full-season statistics
- `team_season_stats` - Team full-season statistics
- `batter_monthly_stats` - Batter monthly breakdown
- `pitcher_monthly_stats` - Pitcher monthly breakdown

## Next Steps

1. **Import Data**: Populate player and stats data into the database with the scraper
2. **Create Admin Endpoints**: Add endpoints for data import/update (if needed)
3. **Add Authentication**: Implement API key or JWT authentication
4. **Add Testing**: Create unit and integration tests
5. **Deploy**: Use Docker or deploy to cloud service (AWS, GCP, Azure, etc.)

## Troubleshooting

### Database lock errors
- Stop the server (Ctrl+C)
- Delete `/app/data/baseball.db`
- Run the scraper again, then restart the server

### CORS errors in frontend
- Ensure `CORS_ORIGINS` includes your frontend URL
- Check `.env` file for correct CORS configuration

### Port already in use
- Use a different port: `uvicorn app.main:app --port 8001`
- Or kill the process using port 8000

## API Documentation

Once the server is running, visit http://localhost:8000/docs for:
- Complete endpoint documentation
- Request/response schemas
- Built-in testing interface
- Parameter descriptions
