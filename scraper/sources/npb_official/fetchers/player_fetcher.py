"""Fetcher for individual NPB player pages."""

import time
import logging
import requests

from scraper.config import (
    NPB_BASE_URL, REQUEST_TIMEOUT, REQUEST_DELAY,
    USER_AGENT, RAW_DATA_DIR, ENCODING_PRIORITY
)

logger = logging.getLogger(__name__)


class PlayerFetcher:
    """Fetches individual player pages from NPB official website."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.base_url = NPB_BASE_URL
        self.raw_data_dir = RAW_DATA_DIR

    def fetch_player(self, npb_player_id: str) -> str:
        """
        Fetch individual player page.

        Args:
            npb_player_id: NPB player ID

        Returns:
            HTML content as string
        """
        url = f"{self.base_url}/players/{npb_player_id}.html"
        logger.info(f"Fetching player: {npb_player_id} from {url}")

        html = self._fetch_url(url)

        # Save raw HTML
        output_path = self.raw_data_dir / "players" / f"{npb_player_id}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Saved raw HTML to {output_path}")

        return html

    def fetch_players(self, npb_player_ids: list) -> dict:
        """
        Fetch multiple player pages.

        Args:
            npb_player_ids: List of NPB player IDs

        Returns:
            Dictionary with player IDs as keys and HTML content as values
        """
        results = {}
        for player_id in npb_player_ids:
            try:
                html = self.fetch_player(player_id)
                results[player_id] = html
                time.sleep(REQUEST_DELAY)
            except Exception as e:
                logger.error(f"Error fetching player {player_id}: {e}")

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
