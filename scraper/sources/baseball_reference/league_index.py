"""Discover Baseball Reference league IDs for each NPB season.

Baseball Reference uses opaque IDs (e.g. ``5677b62d``) for each league /
season combination.  The "Foreign League Encyclopedia" pages list every
historical season with a link to its stats page.

Central League encyclopedia:
  https://www.baseball-reference.com/register/league.cgi?code=JPCL&class=Fgn

Pacific League encyclopedia:
  https://www.baseball-reference.com/register/league.cgi?code=JPPL&class=Fgn

This module fetches those pages once, caches the year→ID mappings in
memory, and exposes them to the rest of the scraper.
"""

import logging
import re
from typing import Dict, Optional, Tuple

from .fetcher import BaseballReferenceFetcher

logger = logging.getLogger(__name__)

BASE_URL = "https://www.baseball-reference.com"

# Encyclopedia page URLs
_ENCYCLOPEDIA_URLS: Dict[str, str] = {
    "central": f"{BASE_URL}/register/league.cgi?code=JPCL&class=Fgn",
    "pacific": f"{BASE_URL}/register/league.cgi?code=JPPL&class=Fgn",
}

# Fallback hard-coded IDs in case the encyclopedia page structure changes.
# Keys are (year, league) tuples.
_FALLBACK_IDS: Dict[Tuple[int, str], str] = {
    (2024, "central"): "5e1f8b77",
    (2024, "pacific"): "5677b62d",
    (2023, "central"): "",  # fill in if known
    (2023, "pacific"): "",
    (2022, "central"): "",
    (2022, "pacific"): "",
    (2021, "central"): "",
    (2021, "pacific"): "",
    (2020, "central"): "",
    (2020, "pacific"): "",
}

# ID pattern found in href attributes of anchor tags on the encyclopedia page
_ID_PATTERN = re.compile(r"league\.cgi\?id=([0-9a-f]+)")


class LeagueIndex:
    """Cache of year → league_id mappings for the NPB Central and Pacific leagues."""

    def __init__(self, fetcher: Optional[BaseballReferenceFetcher] = None):
        self.fetcher = fetcher or BaseballReferenceFetcher()
        # {(year, league): league_id}
        self._cache: Dict[Tuple[int, str], str] = {}
        self._loaded: Dict[str, bool] = {"central": False, "pacific": False}

    def get_league_id(self, year: int, league: str) -> Optional[str]:
        """Return the Baseball Reference league ID for *year* and *league*.

        *league* must be ``"central"`` or ``"pacific"``.
        Raises ``ValueError`` for unknown leagues.
        """
        league = league.lower()
        if league not in ("central", "pacific"):
            raise ValueError(f"Unknown league: {league!r}. Use 'central' or 'pacific'.")

        # Load from encyclopedia page if not done yet
        if not self._loaded[league]:
            self._load_encyclopedia(league)

        result = self._cache.get((year, league))
        if not result:
            # Try fallback
            result = _FALLBACK_IDS.get((year, league)) or None
            if result:
                logger.info(
                    "Using fallback league ID for %d %s: %s", year, league, result
                )
        return result or None

    def get_season_url(self, year: int, league: str) -> Optional[str]:
        """Return the full URL for the season stats page, or None if unknown."""
        league_id = self.get_league_id(year, league)
        if not league_id:
            logger.warning("No league ID found for %d %s", year, league)
            return None
        return f"{BASE_URL}/register/league.cgi?id={league_id}"

    # ------------------------------------------------------------------

    def _load_encyclopedia(self, league: str) -> None:
        """Fetch the encyclopedia page and populate *self._cache* for *league*."""
        url = _ENCYCLOPEDIA_URLS[league]
        logger.info("Loading %s league index from %s", league, url)
        soup = self.fetcher.get_soup(url)
        if soup is None:
            logger.error("Could not load league index for %s", league)
            self._loaded[league] = True  # mark as attempted to avoid retry loop
            return

        count = 0
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            m = _ID_PATTERN.search(href)
            if not m:
                continue
            league_id = m.group(1)

            # Try to find the year from the surrounding text
            # The anchor text is usually just the year (e.g. "2024")
            text = a_tag.get_text(strip=True)
            if re.fullmatch(r"\d{4}", text):
                year = int(text)
                self._cache[(year, league)] = league_id
                count += 1

        logger.info("Loaded %d %s league season IDs", count, league)
        self._loaded[league] = True
