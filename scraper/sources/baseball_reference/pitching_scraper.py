"""Pitching statistics scraper for Baseball Reference NPB pages."""

import logging
from io import StringIO
from typing import Dict, List, Optional

import pandas as pd

from .fetcher import BaseballReferenceFetcher
from .league_index import LeagueIndex

logger = logging.getLogger(__name__)

# Mapping: Baseball Reference column name → our DB field name
_PITCHING_COL_MAP: Dict[str, str] = {
    "Name": "name_en",
    "Tm": "team_name",
    "W": "wins",
    "L": "losses",
    "ERA": "era",
    "G": "games",
    "GS": "games_started",
    "SV": "saves",
    "HLD": "holds",
    "BS": None,      # blown saves — not stored
    "IP": "innings_pitched",
    "H": "hits_allowed",
    "R": "runs_allowed",
    "ER": "earned_runs",
    "HR": "home_runs_allowed",
    "BB": "walks_allowed",
    "SO": "strikeouts",
    "WHIP": "whip",
    # Some pages label holds differently
    "HLD ": "holds",
}

_FLOAT_COLS = {"era", "innings_pitched", "whip"}

_PITCHING_TABLE_IDS = [
    "pitching_standard",
    "standard_pitching",
    "team_pitching",
]


class PitchingScraper:
    """Fetches and parses pitching statistics from Baseball Reference."""

    def __init__(
        self,
        fetcher: Optional[BaseballReferenceFetcher] = None,
        league_index: Optional[LeagueIndex] = None,
    ):
        self.fetcher = fetcher or BaseballReferenceFetcher()
        self.league_index = league_index or LeagueIndex(self.fetcher)

    def scrape_year(self, year: int) -> List[Dict]:
        """Scrape pitching stats for both leagues for *year*.

        Returns a list of normalised record dicts.
        """
        records: List[Dict] = []
        for league in ("central", "pacific"):
            url = self.league_index.get_season_url(year, league)
            if not url:
                logger.warning("Skipping %d %s pitching (no URL)", year, league)
                continue
            logger.info("Scraping %d %s pitching from %s", year, league, url)
            league_records = self._scrape_url(url, year, league)
            records.extend(league_records)
            logger.info(
                "Got %d pitching records for %d %s", len(league_records), year, league
            )
        return records

    # ------------------------------------------------------------------

    def _scrape_url(self, url: str, year: int, league: str) -> List[Dict]:
        soup = self.fetcher.get_soup(url)
        if soup is None:
            return []

        table = None
        for tid in _PITCHING_TABLE_IDS:
            table = soup.find("table", {"id": tid})
            if table:
                logger.debug("Found pitching table '%s' on %s", tid, url)
                break

        if table is None:
            for t in soup.find_all("table"):
                headers = [th.get_text(strip=True) for th in t.find_all("th")]
                if "Name" in headers and "ERA" in headers:
                    table = t
                    logger.debug("Using fallback pitching table on %s", url)
                    break

        if table is None:
            logger.error("No pitching table found on %s", url)
            return []

        try:
            df = pd.read_html(StringIO(str(table)))[0]
        except Exception as exc:
            logger.error("Failed to parse pitching table: %s", exc)
            return []

        return self._parse_df(df, year, league)

    def _parse_df(self, df: pd.DataFrame, year: int, league: str) -> List[Dict]:
        records: List[Dict] = []

        if "Name" in df.columns:
            df = df[df["Name"] != "Name"].copy()
            df = df[df["Name"].notna() & (df["Name"].str.strip() != "")].copy()

        rename_map = {br: db for br, db in _PITCHING_COL_MAP.items()
                      if br in df.columns and db is not None}
        df = df.rename(columns=rename_map)

        for _, row in df.iterrows():
            name = str(row.get("name_en", "")).strip()
            if not name or name.lower() in ("", "nan"):
                continue

            record: Dict = {
                "year": year,
                "league": league,
                "name_en": name,
                "team_name": str(row.get("team_name", "")).strip(),
            }

            int_fields = [
                "wins", "losses", "games", "games_started", "saves", "holds",
                "hits_allowed", "runs_allowed", "earned_runs",
                "home_runs_allowed", "walks_allowed", "strikeouts",
            ]
            for field in int_fields:
                record[field] = _parse_int(row.get(field))

            for field in _FLOAT_COLS:
                record[field] = _parse_float(row.get(field))

            records.append(record)

        return records


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_int(val) -> Optional[int]:
    try:
        return int(float(str(val).replace(",", "")))
    except (ValueError, TypeError):
        return None


def _parse_float(val) -> Optional[float]:
    try:
        s = str(val).strip()
        if s in ("", "nan", "---", "N/A"):
            return None
        return float(s)
    except (ValueError, TypeError):
        return None
