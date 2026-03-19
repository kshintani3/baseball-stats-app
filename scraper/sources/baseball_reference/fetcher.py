"""HTTP fetcher for Baseball Reference pages.

Baseball Reference wraps many of its stats tables inside HTML comments
(<!-- ... -->) to prevent naïve scrapers.  We need to strip those
comment markers before feeding the HTML into BeautifulSoup / pandas.
"""

import logging
import time
from io import StringIO
from typing import Optional

import requests
from bs4 import BeautifulSoup, Comment

logger = logging.getLogger(__name__)

# Baseball Reference asks for a reasonable User-Agent and rate-limiting.
# Keeping REQUEST_DELAY >= 3 s is strongly recommended.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; personal-stats-bot/1.0; "
    "+https://github.com/your-repo)"
)
REQUEST_DELAY = 3  # seconds between HTTP requests
REQUEST_TIMEOUT = 30


class BaseballReferenceFetcher:
    """Fetches and pre-processes HTML pages from Baseball Reference."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        request_delay: float = REQUEST_DELAY,
        request_timeout: int = REQUEST_TIMEOUT,
    ):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.request_delay = request_delay
        self.request_timeout = request_timeout
        self._last_request_time: float = 0.0

    def _throttle(self) -> None:
        """Sleep if the minimum interval between requests has not elapsed."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)

    def fetch_html(self, url: str) -> Optional[str]:
        """Fetch raw HTML from *url*, with throttling and error handling.

        Returns the decoded HTML string, or None on failure.
        """
        self._throttle()
        try:
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()
            self._last_request_time = time.time()
            logger.debug("Fetched %s  (%d bytes)", url, len(response.content))
            return response.text
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            return None

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Return a BeautifulSoup object for *url*.

        HTML comments containing ``<table>`` elements are automatically
        uncommented so that BeautifulSoup can find the tables normally.
        """
        html = self.fetch_html(url)
        if html is None:
            return None
        return self._uncomment_tables(html)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _uncomment_tables(html: str) -> BeautifulSoup:
        """Parse *html* and lift any tables that are hidden inside comments.

        Baseball Reference embeds tables as HTML comments like::

            <!-- <table id="batting_standard">...</table> -->

        This method finds those comments, parses the inner HTML, and
        inserts the resulting elements back into the document so they are
        accessible through normal BeautifulSoup queries.
        """
        soup = BeautifulSoup(html, "lxml")
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            if "<table" in comment:
                # Parse the commented HTML and insert its children into the
                # parent element, replacing the comment node.
                inner = BeautifulSoup(comment, "lxml")
                comment.replace_with(inner)
        return soup
