"""Team standings scraper for Baseball Reference NPB pages."""

import logging
from io import StringIO
from typing import Dict, List, Optional

import pandas as pd

from .fetcher import BaseballReferenceFetcher
from .league_index import LeagueIndex

logger = logging.getLogger(__name__)

_STANDINGS_TABLE_IDS = [
    "standings",
    "expanded_standings_overall",
    "team_stats",
]

# Column mapping: Baseball Reference → our DB field names
_TEAM_COL_MAP: Dict[str, str] = {
    "Tm": "team_name",
    "W": "wins",
    "L": "losses",
    "T": "draws",
    "W-L%": "win_pct",
    "R": "runs_scored",
    "RA": "runs_allowed",
    "HR": "home_runs",
    "SB": "stolen_bases",
    "BA": "team_batting_avg",
    "ERA": "team_era",
}

_FLOAT_COLS = {"win_pct", "team_batting_avg", "team_era"}


class TeamScraper:
    """Fetches and parses team standings from Baseball Reference."""

    def __init__(
        self,
        fetcher: Optional[BaseballReferenceFetcher] = None,
        league_index: Optional[LeagueIndex] = None,
    ):
        self.fetcher = fetcher or BaseballReferenceFetcher()
        self.league_index = league_index or LeagueIndex(self.fetcher)

    def scrape_year(self, year: int) -> List[Dict]:
        """Scrape team records for both leagues for *year*."""
        records: List[Dict] = []
        for league in ("central", "pacific"):
            url = self.league_index.get_season_url(year, league)
            if not url:
                logger.warning("Skipping %d %s teams (no URL)", year, league)
                continue
            logger.info("Scraping %d %s team stats from %s", year, league, url)
            league_records = self._scrape_url(url, year, league)
            records.extend(league_records)
            logger.info(
                "Got %d team records for %d %s", len(league_records), year, league
            )
        return records

    # ------------------------------------------------------------------

    def _scrape_url(self, url: str, year: int, league: str) -> List[Dict]:
        soup = self.fetcher.get_soup(url)
        if soup is None:
            return []

        table = None
        for tid in _STANDINGS_TABLE_IDS:
            table = soup.find("table", {"id": tid})
            if table:
                logger.debug("Found standings table '%s'", tid)
                break

        # Fallback: first table with "Tm" and "W" columns
        if table is None:
            for t in soup.find_all("table"):
                headers = [th.get_text(strip=True) for th in t.find_all("th")]
                if "Tm" in headers and "W" in headers and "L" in headers:
                    table = t
                    logger.debug("Using fallback standings table")
                    break

        if table is None:
            logger.error("No standings table found on %s", url)
            return []

        try:
            df = pd.read_html(StringIO(str(table)))[0]
        except Exception as exc:
            logger.error("Failed to parse standings table: %s", exc)
            return []

        return self._parse_df(df, year, league)

    def _parse_df(self, df: pd.DataFrame, year: int, league: str) -> List[Dict]:
        records: List[Dict] = []

        # Drop separator rows (e.g. blank rows or header repeats)
        if "Tm" in df.columns:
            df = df[df["Tm"].notna() & (df["Tm"].str.strip() != "")].copy()
            df = df[df["Tm"] != "Tm"].copy()

        rename_map = {br: db for br, db in _TEAM_COL_MAP.items() if br in df.columns}
        df = df.rename(columns=rename_map)

        for _, row in df.iterrows():
            team_name = str(row.get("team_name", "")).strip()
            if not team_name or team_name.lower() == "nan":
                continue

            record: Dict = {
                "year": year,
                "league": league,
                "team_name": team_name,
            }

            int_fields = [
                "wins", "losses", "draws", "runs_scored", "runs_allowed",
                "home_runs", "stolen_bases",
            ]
            for field in int_fields:
                record[field] = _parse_int(row.get(field))

            # Compute games from W + L + T
            w = record.get("wins") or 0
            l = record.get("losses") or 0
            d = record.get("draws") or 0
            record["games"] = (w + l + d) or None

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
