"""Configuration for the baseball statistics scraper."""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent          # baseball-app/
SCRAPER_DIR  = Path(__file__).parent                 # baseball-app/scraper/
RAW_DATA_DIR        = SCRAPER_DIR / "raw_data"
NORMALIZED_DATA_DIR = SCRAPER_DIR / "normalized_data"

# Database
DB_PATH = PROJECT_ROOT / "data" / "baseball.db"

# ---------------------------------------------------------------------------
# Data source — Baseball Reference
# ---------------------------------------------------------------------------
BR_BASE_URL = "https://www.baseball-reference.com"

# ---------------------------------------------------------------------------
# Data source fallback — NPB official
# ---------------------------------------------------------------------------
NPB_BASE_URL = "https://npb.jp/bis"

# Encyclopedia pages that list every NPB season with clickable links.
# These are used by LeagueIndex to discover year → league_id mappings.
BR_CENTRAL_ENCYCLOPEDIA_URL = (
    f"{BR_BASE_URL}/register/league.cgi?code=JPCL&class=Fgn"
)
BR_PACIFIC_ENCYCLOPEDIA_URL = (
    f"{BR_BASE_URL}/register/league.cgi?code=JPPL&class=Fgn"
)

# ---------------------------------------------------------------------------
# HTTP settings  (keep REQUEST_DELAY >= 3 s to be a good citizen)
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT = 30
REQUEST_DELAY   = 3   # seconds between requests
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

ENCODING_PRIORITY = ["utf-8", "cp932", "shift_jis", "euc-jp"]

# ---------------------------------------------------------------------------
# NPB team name → short code mapping
# Used by the DB loader to find the right team row.
# Keys are substrings of the English team name as it appears on
# Baseball Reference (case-insensitive matching is applied at runtime).
# ---------------------------------------------------------------------------
TEAM_NAME_TO_CODE: dict = {
    # Central League
    "giants":      "g",
    "yomiuri":     "g",
    "巨人":        "g",
    "読売":        "g",
    "ジャイアンツ": "g",
    "tigers":      "t",
    "hanshin":     "t",
    "阪神":        "t",
    "タイガース":   "t",
    "carp":        "c",
    "hiroshima":   "c",
    "広島":        "c",
    "カープ":       "c",
    "dragons":     "d",
    "chunichi":    "d",
    "中日":        "d",
    "ドラゴンズ":   "d",
    "swallows":    "s",
    "yakult":      "s",
    "ヤクルト":     "s",
    "スワローズ":   "s",
    "baystars":    "db",
    "bay stars":   "db",
    "dena":        "db",
    "de na":       "db",
    "横浜dena":     "db",
    "denabaystars":"db",
    "yokohama":    "db",
    "横浜":        "db",
    "ベイスターズ": "db",
    # Pacific League
    "hawks":       "h",
    "softbank":    "h",
    "ソフトバンク": "h",
    "ホークス":     "h",
    "eagles":      "e",
    "rakuten":     "e",
    "楽天":        "e",
    "イーグルス":   "e",
    "lions":       "l",
    "seibu":       "l",
    "西武":        "l",
    "ライオンズ":   "l",
    "marines":     "m",
    "lotte":       "m",
    "ロッテ":       "m",
    "マリーンズ":   "m",
    "fighters":    "f",
    "nippon ham":  "f",
    "nippon-ham":  "f",
    "日本ハム":     "f",
    "ファイターズ": "f",
    "buffaloes":   "b",
    "orix":        "b",
    "オリックス":   "b",
    "バファローズ": "b",
}

TEAM_CODES: dict = {
    "g": "Giants",
    "t": "Tigers",
    "c": "Carp",
    "d": "Dragons",
    "s": "Swallows",
    "db": "BayStars",
    "h": "Hawks",
    "e": "Eagles",
    "l": "Lions",
    "m": "Marines",
    "f": "Fighters",
    "b": "Buffaloes",
}

BATTING_COLUMNS_JP = []
BATTING_COLUMNS_EN = []
PITCHING_COLUMNS_JP = []
PITCHING_COLUMNS_EN = []

# ---------------------------------------------------------------------------
# Scraping options
# ---------------------------------------------------------------------------
ENABLE_CACHING = True    # cache raw HTML to raw_data/ to avoid re-fetching
VERIFY_SSL     = True

# ---------------------------------------------------------------------------
# Ensure output directories exist
# ---------------------------------------------------------------------------
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
NORMALIZED_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
