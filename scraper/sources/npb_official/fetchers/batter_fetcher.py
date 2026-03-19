"""Fetcher for NPB batting statistics."""

import time
import logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup

from scraper.config import (
    NPB_BASE_URL, TEAM_CODES, REQUEST_TIMEOUT, REQUEST_DELAY,
    USER_AGENT, RAW_DATA_DIR, ENCODING_PRIORITY
)

logger = logging.getLogger(__name__)


class BatterFetcher:
    """Fetches batting statistics from NPB official website."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.base_url = NPB_BASE_URL
        self.raw_data_dir = RAW_DATA_DIR

    def fetch_team_batting(self, year: int, team_code: str) -> str:
        """
        Fetch all batting stats for a specific team.

        Args:
            year: Year to fetch (e.g., 2024)
            team_code: Team code (e.g., 'g' for Giants)

        Returns:
            HTML content as string
        """
        url = f"{self.base_url}/{year}/stats/idb1_{team_code}.html"
        logger.info(f"Fetching team batting: {team_code} ({year}) from {url}")

        html = self._fetch_url(url)

        # Save raw HTML
        output_path = self.raw_data_dir / str(year) / f"batting_{team_code}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Saved raw HTML to {output_path}")

        return html

    def fetch_league_batting(self, year: int, league: str) -> str:
        """
        Fetch qualified batting stats for a league.

        Args:
            year: Year to fetch
            league: League code ('c' for Central, 'p' for Pacific)

        Returns:
            HTML content as string
        """
        url = f"{self.base_url}/{year}/stats/bat_{league}.html"
        logger.info(f"Fetching league batting: {league} ({year}) from {url}")

        html = self._fetch_url(url)

        # Save raw HTML
        output_path = self.raw_data_dir / str(year) / f"batting_league_{league}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Saved raw HTML to {output_path}")

        return html

    def fetch_team_batting_stats(self, year: int, league: str) -> str:
        """
        Fetch team-level batting stats.

        Args:
            year: Year to fetch
            league: League code ('c' for Central, 'p' for Pacific)

        Returns:
            HTML content as string
        """
        url = f"{self.base_url}/{year}/stats/tmb_{league}.html"
        logger.info(f"Fetching team batting stats: {league} ({year}) from {url}")

        html = self._fetch_url(url)

        # Save raw HTML
        output_path = self.raw_data_dir / str(year) / f"team_batting_stats_{league}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Saved raw HTML to {output_path}")

        return html

    def fetch_all_batting(self, year: int) -> dict:
        """
        Fetch all batting data for a year.

        Args:
            year: Year to fetch

        Returns:
            Dictionary with 'team_batting' and 'league_batting' keys
        """
        results = {
            'team_batting': {},
            'league_batting': {}
        }

        # Fetch team batting for all teams
        for team_code in TEAM_CODES.keys():
            try:
                html = self.fetch_team_batting(year, team_code)
                results['team_batting'][team_code] = html
                time.sleep(REQUEST_DELAY)
            except Exception as e:
                logger.error(f"Error fetching team batting for {team_code}: {e}")

        # Fetch league batting for both leagues
        for league in ['c', 'p']:
            try:
                html = self.fetch_league_batting(year, league)
                results['league_batting'][league] = html
                time.sleep(REQUEST_DELAY)
            except Exception as e:
                logger.error(f"Error fetching league batting for {league}: {e}")

        return results

    def _fetch_url(self, url: str) -> str:
        """
        Fetch a URL and return HTML content.

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        try:
            response = self.session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                verify=True
            )
            response.raise_for_status()

            # Try to decode with different encodings
            for encoding in ENCODING_PRIORITY:
                try:
                    return response.content.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    continue

            # Fallback to default
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
