"""Fetcher for NPB team standings."""

import time
import logging
import requests

from scraper.config import (
    NPB_BASE_URL, REQUEST_TIMEOUT, REQUEST_DELAY,
    USER_AGENT, RAW_DATA_DIR, ENCODING_PRIORITY
)

logger = logging.getLogger(__name__)


class TeamFetcher:
    """Fetches team standings from NPB official website."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.base_url = NPB_BASE_URL
        self.raw_data_dir = RAW_DATA_DIR

    def fetch_standings(self, year: int) -> str:
        """
        Fetch team standings for a year.

        Args:
            year: Year to fetch (e.g., 2024)

        Returns:
            HTML content as string
        """
        url = f"{self.base_url}/{year}/standings/"
        logger.info(f"Fetching standings: {year} from {url}")

        html = self._fetch_url(url)

        # Save raw HTML
        output_path = self.raw_data_dir / str(year) / "standings.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Saved raw HTML to {output_path}")

        return html

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
