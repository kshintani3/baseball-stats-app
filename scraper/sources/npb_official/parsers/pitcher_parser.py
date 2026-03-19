"""Parser for NPB pitching statistics."""

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PitcherParser:
    """Parses pitching statistics from NPB HTML."""

    @staticmethod
    def parse_team_pitching(html: str, team_code: str, year: int) -> List[Dict[str, Any]]:
        """Parse team pitching data from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        records: List[Dict[str, Any]] = []

        for row in soup.select("tr.ststats"):
            cells = row.find_all("td")
            if len(cells) < 26:
                continue

            player_name = cells[1].get_text(strip=True)
            if not player_name:
                continue

            innings_whole = cells[13].get_text(strip=True)
            innings_frac = cells[14].get_text(strip=True)

            records.append(
                {
                    "year": year,
                    "team_code": team_code,
                    "player_name": player_name,
                    "appearances": PitcherParser._parse_int(cells[2].get_text(strip=True)),
                    "wins": PitcherParser._parse_int(cells[3].get_text(strip=True)),
                    "losses": PitcherParser._parse_int(cells[4].get_text(strip=True)),
                    "saves": PitcherParser._parse_int(cells[5].get_text(strip=True)),
                    "holds": PitcherParser._parse_int(cells[6].get_text(strip=True)),
                    "innings_pitched": PitcherParser._parse_innings(innings_whole, innings_frac),
                    "hits_allowed": PitcherParser._parse_int(cells[15].get_text(strip=True)),
                    "home_runs_allowed": PitcherParser._parse_int(cells[16].get_text(strip=True)),
                    "walks": PitcherParser._parse_int(cells[17].get_text(strip=True)),
                    "strikeouts": PitcherParser._parse_int(cells[20].get_text(strip=True)),
                    "runs_allowed": PitcherParser._parse_int(cells[23].get_text(strip=True)),
                    "earned_runs": PitcherParser._parse_int(cells[24].get_text(strip=True)),
                    "era": PitcherParser._parse_float(cells[25].get_text(strip=True)),
                    "whip": PitcherParser._calc_whip(
                        cells[15].get_text(strip=True),
                        cells[17].get_text(strip=True),
                        innings_whole,
                        innings_frac,
                    ),
                }
            )

        return records

    @staticmethod
    def parse_league_pitching(html: str, league: str, year: int) -> List[Dict[str, Any]]:
        """Parse league pitching data from HTML."""
        return PitcherParser.parse_team_pitching(html, league, year)

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

    @staticmethod
    def _parse_innings(whole: Any, frac: Any) -> float:
        whole_str = str(whole).strip()
        frac_str = str(frac).strip()

        innings = PitcherParser._parse_float(whole_str)
        if frac_str == ".1":
            innings += 1 / 3
        elif frac_str == ".2":
            innings += 2 / 3

        return round(innings, 3)

    @staticmethod
    def _calc_whip(hits: Any, walks: Any, whole: Any, frac: Any) -> float:
        innings = PitcherParser._parse_innings(whole, frac)
        if innings <= 0:
            return 0.0
        hits_allowed = PitcherParser._parse_int(hits)
        walks_allowed = PitcherParser._parse_int(walks)
        return round((hits_allowed + walks_allowed) / innings, 2)
