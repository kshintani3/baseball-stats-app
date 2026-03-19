"""Database loader — writes scraped records to the SQLite database.

This module uses plain synchronous SQLAlchemy (not the async flavour used by
the FastAPI backend) so it can be run as a standalone CLI script without an
event loop.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


_NPB_TEAMS = [
    ("g", "読売ジャイアンツ", "Yomiuri Giants", "Giants", "central"),
    ("t", "阪神タイガース", "Hanshin Tigers", "Tigers", "central"),
    ("c", "広島東洋カープ", "Hiroshima Carp", "Carp", "central"),
    ("d", "中日ドラゴンズ", "Chunichi Dragons", "Dragons", "central"),
    ("s", "東京ヤクルトスワローズ", "Tokyo Yakult Swallows", "Swallows", "central"),
    ("db", "横浜DeNAベイスターズ", "Yokohama DeNA BayStars", "BayStars", "central"),
    ("h", "福岡ソフトバンクホークス", "Fukuoka SoftBank Hawks", "Hawks", "pacific"),
    ("e", "東北楽天ゴールデンイーグルス", "Tohoku Rakuten Golden Eagles", "Eagles", "pacific"),
    ("l", "埼玉西武ライオンズ", "Saitama Seibu Lions", "Lions", "pacific"),
    ("m", "千葉ロッテマリーンズ", "Chiba Lotte Marines", "Marines", "pacific"),
    ("f", "北海道日本ハムファイターズ", "Hokkaido Nippon Ham Fighters", "Fighters", "pacific"),
    ("b", "オリックス・バファローズ", "Orix Buffaloes", "Buffaloes", "pacific"),
]


# ---------------------------------------------------------------------------
# Team name → code helper
# ---------------------------------------------------------------------------

def _team_code_from_name(team_name: str, name_map: Dict[str, str]) -> Optional[str]:
    """Return the team code for *team_name* using substring matching."""
    name_lower = team_name.lower().replace("-", " ")
    for keyword, code in name_map.items():
        if keyword in name_lower:
            return code
    return None


# ---------------------------------------------------------------------------
# Main loader class
# ---------------------------------------------------------------------------

class DatabaseLoader:
    """Loads scraped stats into the SQLite database."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._team_name_map: Dict[str, str] = {}
        self._team_id_cache: Dict[str, int] = {}  # team_code → DB id

        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            self.engine = create_engine(
                f"sqlite:///{db_path}",
                echo=False,
                connect_args={"check_same_thread": False},
            )
            self.SessionLocal = sessionmaker(
                bind=self.engine, autocommit=False, autoflush=False
            )
        except ImportError as exc:
            logger.error("SQLAlchemy is not installed: %s", exc)
            raise

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_batting_stats(self, records: List[Dict[str, Any]]) -> int:
        """Upsert batting statistics into batter_season_stats."""
        return self._load_player_stats(records, stat_type="batting")

    def load_pitching_stats(self, records: List[Dict[str, Any]]) -> int:
        """Upsert pitching statistics into pitcher_season_stats."""
        return self._load_player_stats(records, stat_type="pitching")

    def load_team_stats(self, records: List[Dict[str, Any]]) -> int:
        """Upsert team statistics into team_season_stats."""
        from sqlalchemy import text

        session = self.SessionLocal()
        count = 0
        try:
            self._ensure_team_cache(session)

            for rec in records:
                team_code = self._resolve_team_code(rec.get("team_name", ""))
                if not team_code:
                    logger.warning("Unknown team: %s", rec.get("team_name"))
                    continue
                team_db_id = self._team_id_cache.get(team_code)
                if not team_db_id:
                    logger.warning("Team code '%s' not in DB", team_code)
                    continue

                year = rec.get("year")
                if not year:
                    continue

                existing = session.execute(
                    text(
                        "SELECT id FROM team_season_stats "
                        "WHERE team_id=:tid AND season=:season"
                    ),
                    {"tid": team_db_id, "season": year},
                ).fetchone()

                row: Dict[str, Any] = {
                    "team_id": team_db_id,
                    "season": year,
                    "games": rec.get("games"),
                    "wins": rec.get("wins"),
                    "losses": rec.get("losses"),
                    "draws": rec.get("draws"),
                    "win_pct": rec.get("win_pct"),
                    "runs_scored": rec.get("runs_scored"),
                    "runs_allowed": rec.get("runs_allowed"),
                    "home_runs": rec.get("home_runs"),
                    "stolen_bases": rec.get("stolen_bases"),
                    "team_batting_avg": rec.get("team_batting_avg"),
                    "team_era": rec.get("team_era"),
                    "created_at": _now(),
                    "updated_at": _now(),
                }

                if existing:
                    row["id"] = existing[0]
                    session.execute(
                        text(
                            "UPDATE team_season_stats SET "
                            "games=:games, wins=:wins, losses=:losses, draws=:draws, "
                            "win_pct=:win_pct, runs_scored=:runs_scored, "
                            "runs_allowed=:runs_allowed, home_runs=:home_runs, "
                            "stolen_bases=:stolen_bases, team_batting_avg=:team_batting_avg, "
                            "team_era=:team_era, updated_at=:updated_at "
                            "WHERE id=:id"
                        ),
                        row,
                    )
                else:
                    session.execute(
                        text(
                            "INSERT INTO team_season_stats "
                            "(team_id, season, games, wins, losses, draws, win_pct, "
                            "runs_scored, runs_allowed, home_runs, stolen_bases, "
                            "team_batting_avg, team_era, created_at, updated_at) VALUES "
                            "(:team_id, :season, :games, :wins, :losses, :draws, :win_pct, "
                            ":runs_scored, :runs_allowed, :home_runs, :stolen_bases, "
                            ":team_batting_avg, :team_era, :created_at, :updated_at)"
                        ),
                        row,
                    )
                count += 1

            session.commit()
            logger.info("Loaded %d team stats records", count)
        except Exception as exc:
            session.rollback()
            logger.error("Error loading team stats: %s", exc, exc_info=True)
        finally:
            session.close()
        return count

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_player_stats(self, records: List[Dict[str, Any]], stat_type: str) -> int:
        """Generic upsert for batter_season_stats or pitcher_season_stats."""
        from sqlalchemy import text

        table = "batter_season_stats" if stat_type == "batting" else "pitcher_season_stats"

        session = self.SessionLocal()
        count = 0
        try:
            self._ensure_team_cache(session)

            for rec in records:
                year = rec.get("year")
                name_en = str(rec.get("name_en") or rec.get("player_name") or "").strip()
                if not name_en or not year:
                    continue

                team_code = rec.get("team_code") or self._resolve_team_code(rec.get("team_name", ""))
                team_db_id = self._team_id_cache.get(team_code) if team_code else None

                player_id = self._upsert_player(session, name_en, team_db_id)
                if not player_id:
                    continue

                # Build stat row
                if stat_type == "batting":
                    stat_row = self._batting_row(rec, player_id, year)
                else:
                    stat_row = self._pitching_row(rec, player_id, year)

                existing = session.execute(
                    text(
                        f"SELECT id FROM {table} "
                        "WHERE player_id=:player_id AND season=:season"
                    ),
                    {"player_id": player_id, "season": year},
                ).fetchone()

                cols = list(stat_row.keys())
                update_cols = [c for c in cols if c not in ("player_id", "season", "created_at")]

                if existing:
                    stat_row["id"] = existing[0]
                    sets = ", ".join(f"{c}=:{c}" for c in update_cols)
                    session.execute(
                        text(f"UPDATE {table} SET {sets} WHERE id=:id"),
                        stat_row,
                    )
                else:
                    col_list = ", ".join(cols)
                    placeholders = ", ".join(f":{c}" for c in cols)
                    session.execute(
                        text(f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"),
                        stat_row,
                    )
                count += 1

            session.commit()
            logger.info("Loaded %d %s records", count, stat_type)
        except Exception as exc:
            session.rollback()
            logger.error("Error loading %s stats: %s", stat_type, exc, exc_info=True)
        finally:
            session.close()
        return count

    def _ensure_team_cache(self, session) -> None:
        """Populate _team_id_cache from the DB teams table."""
        if self._team_id_cache:
            return
        from sqlalchemy import text

        self._ensure_schema(session)

        rows = session.execute(text("SELECT id, code FROM teams")).fetchall()
        for db_id, code in rows:
            self._team_id_cache[code] = db_id

        try:
            from scraper.config import TEAM_NAME_TO_CODE
            self._team_name_map = TEAM_NAME_TO_CODE
        except ImportError:
            # Inline fallback so the loader works even without scraper.config
            self._team_name_map = {
                "giants": "g", "yomiuri": "g",
                "tigers": "t", "hanshin": "t",
                "carp": "c", "hiroshima": "c",
                "dragons": "d", "chunichi": "d",
                "swallows": "s", "yakult": "s",
                "baystars": "db", "bay stars": "db", "dena": "db", "yokohama": "db",
                "hawks": "h", "softbank": "h",
                "eagles": "e", "rakuten": "e",
                "lions": "l", "seibu": "l",
                "marines": "m", "lotte": "m",
                "fighters": "f", "nippon ham": "f", "nippon-ham": "f",
                "buffaloes": "b", "orix": "b",
            }

    def _resolve_team_code(self, team_name: str) -> Optional[str]:
        return _team_code_from_name(team_name, self._team_name_map)

    def _ensure_schema(self, session) -> None:
        """Create the minimal schema required by the standalone scraper."""
        from sqlalchemy import text

        session.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(10) NOT NULL UNIQUE,
                    name_ja VARCHAR(200) NOT NULL,
                    name_en VARCHAR(200) NOT NULL,
                    short_name VARCHAR(50) NOT NULL,
                    league VARCHAR(20) NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
        )
        session.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    npb_id VARCHAR(50) NOT NULL UNIQUE,
                    name_ja VARCHAR(200) NOT NULL,
                    name_en VARCHAR(200) NOT NULL,
                    team_id INTEGER NOT NULL,
                    position VARCHAR(20),
                    bats VARCHAR(1),
                    throws VARCHAR(1),
                    birth_date DATE,
                    jersey_number INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY(team_id) REFERENCES teams(id)
                )
                """
            )
        )
        session.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS batter_season_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    games INTEGER,
                    plate_appearances INTEGER,
                    at_bats INTEGER,
                    hits INTEGER,
                    doubles INTEGER,
                    triples INTEGER,
                    home_runs INTEGER,
                    rbi INTEGER,
                    runs INTEGER,
                    strikeouts INTEGER,
                    walks INTEGER,
                    hit_by_pitch INTEGER,
                    stolen_bases INTEGER,
                    batting_average FLOAT,
                    on_base_pct FLOAT,
                    slugging_pct FLOAT,
                    ops FLOAT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY(player_id) REFERENCES players(id)
                )
                """
            )
        )
        session.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS pitcher_season_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    games INTEGER,
                    games_started INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    saves INTEGER,
                    holds INTEGER,
                    innings_pitched FLOAT,
                    hits_allowed INTEGER,
                    home_runs_allowed INTEGER,
                    strikeouts INTEGER,
                    walks_allowed INTEGER,
                    runs_allowed INTEGER,
                    earned_runs INTEGER,
                    era FLOAT,
                    whip FLOAT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY(player_id) REFERENCES players(id)
                )
                """
            )
        )
        session.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS team_season_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    games INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    draws INTEGER,
                    win_pct FLOAT,
                    runs_scored INTEGER,
                    runs_allowed INTEGER,
                    home_runs INTEGER,
                    stolen_bases INTEGER,
                    team_batting_avg FLOAT,
                    team_era FLOAT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    FOREIGN KEY(team_id) REFERENCES teams(id)
                )
                """
            )
        )

        existing_team_count = session.execute(
            text("SELECT COUNT(*) FROM teams")
        ).scalar() or 0
        if existing_team_count == 0:
            now = _now()
            session.execute(
                text(
                    """
                    INSERT INTO teams
                    (code, name_ja, name_en, short_name, league, created_at, updated_at)
                    VALUES
                    (:code, :name_ja, :name_en, :short_name, :league, :created_at, :updated_at)
                    """
                ),
                [
                    {
                        "code": code,
                        "name_ja": name_ja,
                        "name_en": name_en,
                        "short_name": short_name,
                        "league": league,
                        "created_at": now,
                        "updated_at": now,
                    }
                    for code, name_ja, name_en, short_name, league in _NPB_TEAMS
                ],
            )
        session.commit()

    def _upsert_player(
        self,
        session,
        name_en: str,
        team_db_id: Optional[int],
    ) -> Optional[int]:
        """Return the player's DB id, creating a new row if needed."""
        from sqlalchemy import text

        npb_id = "br_" + _slugify(name_en)

        row = session.execute(
            text("SELECT id, team_id FROM players WHERE npb_id=:npb_id"),
            {"npb_id": npb_id},
        ).fetchone()

        if row:
            player_id, current_team_id = row
            if team_db_id and team_db_id != current_team_id:
                session.execute(
                    text(
                        "UPDATE players SET team_id=:tid, updated_at=:now WHERE id=:id"
                    ),
                    {"tid": team_db_id, "now": _now(), "id": player_id},
                )
            return player_id

        if not team_db_id:
            logger.warning("No team for '%s' — skipping", name_en)
            return None

        session.execute(
            text(
                "INSERT INTO players "
                "(npb_id, name_ja, name_en, team_id, is_active, created_at, updated_at) "
                "VALUES (:npb_id, :name_ja, :name_en, :team_id, 1, :created_at, :updated_at)"
            ),
            {
                "npb_id": npb_id,
                "name_ja": name_en,   # only English name available from BR
                "name_en": name_en,
                "team_id": team_db_id,
                "created_at": _now(),
                "updated_at": _now(),
            },
        )
        result = session.execute(
            text("SELECT id FROM players WHERE npb_id=:npb_id"),
            {"npb_id": npb_id},
        ).fetchone()
        return result[0] if result else None

    # ------------------------------------------------------------------
    # Row builders
    # ------------------------------------------------------------------

    @staticmethod
    def _batting_row(rec: Dict, player_id: int, year: int) -> Dict[str, Any]:
        return {
            "player_id": player_id,
            "season": year,
            "games": rec.get("games"),
            "plate_appearances": rec.get("plate_appearances"),
            "at_bats": rec.get("at_bats"),
            "hits": rec.get("hits"),
            "doubles": rec.get("doubles"),
            "triples": rec.get("triples"),
            "home_runs": rec.get("home_runs"),
            "rbi": rec.get("rbi"),
            "runs": rec.get("runs"),
            "strikeouts": rec.get("strikeouts"),
            "walks": rec.get("walks"),
            "hit_by_pitch": rec.get("hit_by_pitch"),
            "stolen_bases": rec.get("stolen_bases"),
            "batting_average": rec.get("batting_average", rec.get("batting_avg")),
            "on_base_pct": rec.get("on_base_pct", rec.get("obp")),
            "slugging_pct": rec.get("slugging_pct"),
            "ops": rec.get("ops"),
            "created_at": _now(),
            "updated_at": _now(),
        }

    @staticmethod
    def _pitching_row(rec: Dict, player_id: int, year: int) -> Dict[str, Any]:
        return {
            "player_id": player_id,
            "season": year,
            "games": rec.get("games", rec.get("appearances")),
            "games_started": rec.get("games_started", rec.get("starts")),
            "wins": rec.get("wins"),
            "losses": rec.get("losses"),
            "saves": rec.get("saves"),
            "holds": rec.get("holds"),
            "innings_pitched": rec.get("innings_pitched"),
            "hits_allowed": rec.get("hits_allowed"),
            "home_runs_allowed": rec.get("home_runs_allowed"),
            "strikeouts": rec.get("strikeouts"),
            "walks_allowed": rec.get("walks_allowed", rec.get("walks")),
            "runs_allowed": rec.get("runs_allowed"),
            "earned_runs": rec.get("earned_runs"),
            "era": rec.get("era"),
            "whip": rec.get("whip"),
            "created_at": _now(),
            "updated_at": _now(),
        }


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = slug.replace("\u3000", " ")
    slug = re.sub(r"\s+", "_", slug)
    slug = re.sub(r"[^\w]+", "_", slug, flags=re.UNICODE)
    return slug.strip("_")
