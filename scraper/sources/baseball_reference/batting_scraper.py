"""Batting statistics scraper for Baseball Reference NPB pages."""

import logging
import re
from io import StringIO
from typing import Dict, List, Optional

import pandas as pd

from .fetcher import BaseballReferenceFetcher
from .league_index import LeagueIndex

logger = logging.getLogger(__name__)

# Mapping from Baseball Reference column names → our DB field names.
# Columns absent from a page are simply skipped.
_BATTING_COL_MAP: Dict[str, str] = {
    "Name": "name_en",
    "Tm": "team_name",
    "G": "games",
    "PA": "plate_appearances",
    "AB": "at_bats",
    "R": "runs",
    "H": "hits",
    "2B": "doubles",
    "3B": "triples",
    "HR": "home_runs",
    "RBI": "rbi",
    "SB": "stolen_bases",
    "BB": "walks",
    "SO": "strikeouts",
    "HBP": "hit_by_pitch",
    "BA": "batting_average",
    "OBP": "on_base_pct",
    "SLG": "slugging_pct",
    "OPS": "ops",
}

# Which columns hold floating-point values
_FLOAT_COLS = {"batting_average", "on_base_pct", "slugging_pct", "ops"}

# Table IDs typically used on Baseball Reference league pages for batting
_BATTING_TABLE_IDS = [
    "batting_standard",  # most common
    "standard_batting",
    "team_batting",
]


class BattingScraper:
    """Fetches and parses batting statistics from Baseball Reference."""

    def __init__(
        self,
        fetcher: Optional[BaseballReferenceFetcher] = None,
        league_index: Optional[LeagueIndex] = None,
    ):
        self.fetcher = fetcher or BaseballReferenceFetcher()
        self.league_index = league_index or LeagueIndex(self.fetcher)

    def scrape_year(self, year: int) -> List[Dict]:
        """Scrape batting stats for both leagues for *year*.

        Returns a list of normalised record dicts ready for the DB loader.
        """
        records: List[Dict] = []
        for league in ("central", "pacific"):
            url = self.league_index.get_season_url(year, league)
            if not url:
                logger.warning("Skipping %d %s batting (no URL)", year, league)
                continue
            logger.info("Scraping %d %s batting from %s", year, league, url)
            league_records = self._scrape_url(url, year, league)
            records.extend(league_records)
            logger.info(
                "Got %d batting records for %d %s", len(league_records), year, league
            )
        return records

    # ------------------------------------------------------------------

    def _scrape_url(self, url: str, year: int, league: str) -> List[Dict]:
        """Fetch *url* and extract batting rows."""
        soup = self.fetcher.get_soup(url)
        if soup is None:
            return []

        # Try known table IDs first
        table = None
        for tid in _BATTING_TABLE_IDS:
            table = soup.find("table", {"id": tid})
            if table:
                logger.debug("Found batting table '%s' on %s", tid, url)
                break

        # Fallback: grab the first table on the page that has a "Name" column
        if table is None:
            for t in soup.find_all("table"):
                headers = [th.get_text(strip=True) for th in t.find_all("th")]
                if "Name" in headers and "PA" in headers:
                    table = t
                    logger.debug("Using fallback table on %s", url)
                    break

        if table is None:
            logger.error("No batting table found on %s", url)
            return []

        try:
            df = pd.read_html(StringIO(str(table)))[0]
        except Exception as exc:
            logger.error("Failed to parse batting table: %s", exc)
            return []

        return self._parse_df(df, year, league)

    def _parse_df(self, df: pd.DataFrame, year: int, league: str) -> List[Dict]:
        """Convert a raw DataFrame into a list of normalised record dicts."""
        records: List[Dict] = []

        # Drop header-repeat rows (Baseball Reference repeats column headers
        # partway through long tables; they have "Name" in the Name column)
        if "Name" in df.columns:
            df = df[df["Name"] != "Name"].copy()
            # Drop rows with missing names
            df = df[df["Name"].notna() & (df["Name"].str.strip() != "")].copy()

        # Rename columns we care about
        rename_map = {br: db for br, db in _BATTING_COL_MAP.items() if br in df.columns}
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

            # Integer fields
            int_fields = [
                "games", "plate_appearances", "at_bats", "runs", "hits",
                "doubles", "triples", "home_runs", "rbi", "stolen_bases",
                "walks", "strikeouts", "hit_by_pitch",
            ]
            for field in int_fields:
                val = row.get(field)
                record[field] = _parse_int(val)

            # Float fields
            for field in _FLOAT_COLS:
                val = row.get(field)
                record[field] = _parse_float(val)

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
