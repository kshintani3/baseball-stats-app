"""Command-line interface for the Baseball Reference NPB scraper."""

import argparse
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — works whether called from scraper/ or baseball-app/
# ---------------------------------------------------------------------------
_scraper_dir  = Path(__file__).resolve().parent   # baseball-app/scraper/
_project_root = _scraper_dir.parent               # baseball-app/
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# ---------------------------------------------------------------------------
# Imports (after path setup)
# ---------------------------------------------------------------------------
from scraper.config import DB_PATH
from scraper.sources.baseball_reference.fetcher       import BaseballReferenceFetcher
from scraper.sources.baseball_reference.league_index  import LeagueIndex
from scraper.sources.baseball_reference.batting_scraper   import BattingScraper
from scraper.sources.baseball_reference.pitching_scraper  import PitchingScraper
from scraper.sources.baseball_reference.team_scraper      import TeamScraper
from scraper.sources.npb_official.fetchers.batter_fetcher import BatterFetcher
from scraper.sources.npb_official.fetchers.pitcher_fetcher import PitcherFetcher
from scraper.sources.npb_official.fetchers.team_fetcher import TeamFetcher
from scraper.sources.npb_official.parsers.batter_parser import BatterParser
from scraper.sources.npb_official.parsers.pitcher_parser import PitcherParser
from scraper.sources.npb_official.parsers.team_parser import TeamParser
from scraper.loaders.db_loader import DatabaseLoader

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger("npb-scraper")


# ---------------------------------------------------------------------------
# CLI class
# ---------------------------------------------------------------------------

class ScraperCLI:
    """Orchestrates fetch + DB-load for one or multiple seasons."""

    def __init__(self):
        fetcher          = BaseballReferenceFetcher()
        league_index     = LeagueIndex(fetcher)
        self.batting_sc  = BattingScraper(fetcher, league_index)
        self.pitching_sc = PitchingScraper(fetcher, league_index)
        self.team_sc     = TeamScraper(fetcher, league_index)
        self.npb_batter_fetcher = BatterFetcher()
        self.npb_pitcher_fetcher = PitcherFetcher()
        self.npb_team_fetcher = TeamFetcher()
        self.loader      = DatabaseLoader(DB_PATH)

    def fetch_and_load(self, year: int, data_type: str = "all") -> None:
        """Scrape Baseball Reference for *year* and write to the DB.

        *data_type*: ``all`` | ``batters`` | ``pitchers`` | ``teams``
        """
        logger.info("=== Starting fetch+load  year=%d  type=%s ===", year, data_type)

        if data_type in ("all", "batters"):
            records = self.batting_sc.scrape_year(year)
            if not records:
                logger.info("Baseball Reference batting scrape returned 0 rows; falling back to NPB official")
                records = self._fetch_batters_from_npb_official(year)
            logger.info("Fetched %d batting records — writing to DB…", len(records))
            n = self.loader.load_batting_stats(records)
            logger.info("Stored %d batting records for %d", n, year)

        if data_type in ("all", "pitchers"):
            records = self.pitching_sc.scrape_year(year)
            if not records:
                logger.info("Baseball Reference pitching scrape returned 0 rows; falling back to NPB official")
                records = self._fetch_pitchers_from_npb_official(year)
            logger.info("Fetched %d pitching records — writing to DB…", len(records))
            n = self.loader.load_pitching_stats(records)
            logger.info("Stored %d pitching records for %d", n, year)

        if data_type in ("all", "teams"):
            records = self.team_sc.scrape_year(year)
            if not records:
                logger.info("Baseball Reference team scrape returned 0 rows; falling back to NPB official")
                records = self._fetch_teams_from_npb_official(year)
            logger.info("Fetched %d team records — writing to DB…", len(records))
            n = self.loader.load_team_stats(records)
            logger.info("Stored %d team records for %d", n, year)

        logger.info("=== Done  year=%d ===", year)

    def fetch_and_load_range(
        self, start_year: int, end_year: int, data_type: str = "all"
    ) -> None:
        """Scrape and load for every year in [start_year, end_year]."""
        logger.info("Fetching %d–%d  type=%s", start_year, end_year, data_type)
        for year in range(start_year, end_year + 1):
            try:
                self.fetch_and_load(year, data_type)
            except Exception as exc:
                logger.error("Error processing %d: %s", year, exc, exc_info=True)

    def _fetch_batters_from_npb_official(self, year: int) -> list[dict]:
        records: list[dict] = []
        for team_code in ("g", "t", "c", "d", "s", "db", "h", "e", "l", "m", "f", "b"):
            try:
                html = self.npb_batter_fetcher.fetch_team_batting(year, team_code)
                records.extend(BatterParser.parse_team_batting(html, team_code, year))
            except Exception as exc:
                logger.error("NPB official batting fallback failed for %s %d: %s", team_code, year, exc)
        return records

    def _fetch_pitchers_from_npb_official(self, year: int) -> list[dict]:
        records: list[dict] = []
        for team_code in ("g", "t", "c", "d", "s", "db", "h", "e", "l", "m", "f", "b"):
            try:
                html = self.npb_pitcher_fetcher.fetch_team_pitching(year, team_code)
                records.extend(PitcherParser.parse_team_pitching(html, team_code, year))
            except Exception as exc:
                logger.error("NPB official pitching fallback failed for %s %d: %s", team_code, year, exc)
        return records

    def _fetch_teams_from_npb_official(self, year: int) -> list[dict]:
        try:
            html = self.npb_team_fetcher.fetch_standings(year)
            return TeamParser.parse_standings(html, year)
        except Exception as exc:
            logger.error("NPB official team fallback failed for %d: %s", year, exc)
            return []


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="NPB Baseball Statistics Scraper — source: Baseball Reference"
    )
    sub = parser.add_subparsers(dest="command", help="Sub-command")

    # fetch  (single year) ----------------------------------------------------
    p_fetch = sub.add_parser(
        "fetch",
        help="Scrape Baseball Reference for one year and store results in the DB",
    )
    p_fetch.add_argument("--year", type=int, required=True, help="Season year")
    p_fetch.add_argument(
        "--type",
        choices=["all", "batters", "pitchers", "teams"],
        default="all",
        help="Which data to fetch (default: all)",
    )

    # fetch-all  (year range) -------------------------------------------------
    p_all = sub.add_parser(
        "fetch-all",
        help="Scrape Baseball Reference for a range of years",
    )
    p_all.add_argument("--start", type=int, required=True, help="First year")
    p_all.add_argument("--end",   type=int, required=True, help="Last year (inclusive)")
    p_all.add_argument(
        "--type",
        choices=["all", "batters", "pitchers", "teams"],
        default="all",
        help="Which data to fetch (default: all)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = ScraperCLI()

    if args.command == "fetch":
        cli.fetch_and_load(args.year, getattr(args, "type", "all"))
    elif args.command == "fetch-all":
        cli.fetch_and_load_range(
            args.start, args.end, getattr(args, "type", "all")
        )


if __name__ == "__main__":
    main()
