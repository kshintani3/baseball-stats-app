"""Parser for NPB batting statistics."""

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BatterParser:
    """Parses batting statistics from NPB HTML."""

    @staticmethod
    def parse_team_batting(html: str, team_code: str, year: int) -> List[Dict[str, Any]]:
        """Parse team batting data from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        records: List[Dict[str, Any]] = []

        for row in soup.select("tr.ststats"):
            cells = row.find_all("td")
            if len(cells) < 24:
                continue

            player_name = cells[1].get_text(strip=True)
            if not player_name:
                continue

            slugging_pct = BatterParser._parse_float(cells[22].get_text(strip=True))
            obp = BatterParser._parse_float(cells[23].get_text(strip=True))

            records.append(
                {
                    "year": year,
                    "team_code": team_code,
                    "player_name": player_name,
                    "games": BatterParser._parse_int(cells[2].get_text(strip=True)),
                    "plate_appearances": BatterParser._parse_int(cells[3].get_text(strip=True)),
                    "at_bats": BatterParser._parse_int(cells[4].get_text(strip=True)),
                    "runs": BatterParser._parse_int(cells[5].get_text(strip=True)),
                    "hits": BatterParser._parse_int(cells[6].get_text(strip=True)),
                    "doubles": BatterParser._parse_int(cells[7].get_text(strip=True)),
                    "triples": BatterParser._parse_int(cells[8].get_text(strip=True)),
                    "home_runs": BatterParser._parse_int(cells[9].get_text(strip=True)),
                    "rbi": BatterParser._parse_int(cells[11].get_text(strip=True)),
                    "stolen_bases": BatterParser._parse_int(cells[12].get_text(strip=True)),
                    "walks": BatterParser._parse_int(cells[16].get_text(strip=True)),
                    "hit_by_pitch": BatterParser._parse_int(cells[18].get_text(strip=True)),
                    "strikeouts": BatterParser._parse_int(cells[19].get_text(strip=True)),
                    "batting_avg": BatterParser._parse_float(cells[21].get_text(strip=True)),
                    "slugging_pct": slugging_pct,
                    "obp": obp,
                    "ops": round(slugging_pct + obp, 3),
                }
            )

        return records

    @staticmethod
    def parse_league_batting(html: str, league: str, year: int) -> List[Dict[str, Any]]:
        """Parse league batting data from HTML."""
        return BatterParser.parse_team_batting(html, league, year)

    @staticmethod
    def _parse_int(value: Any) -> int:
        try:
            value_str = str(value).strip()
            if not value_str:
                return 0
            return int(float(value_str))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _parse_float(value: Any) -> float:
        try:
            value_str = str(value).strip().replace(",", "")
            if not value_str:
                return 0.0
            if value_str.startswith("."):
                value_str = f"0{value_str}"
            return float(value_str)
        except (ValueError, TypeError):
            return 0.0
