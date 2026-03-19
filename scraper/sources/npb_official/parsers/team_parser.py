"""Parser for NPB team standings."""

import logging
import re
from typing import List, Dict, Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TeamParser:
    """Parses team standings from NPB HTML."""

    @staticmethod
    def parse_standings(html: str, year: int) -> List[Dict[str, Any]]:
        """
        Parse standings data from HTML.

        Args:
            html: HTML content
            year: Year

        Returns:
            List of team standing dictionaries
        """
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.select("table.standingsList")
        records: List[Dict[str, Any]] = []

        for table in tables:
            league = TeamParser._league_from_table(table)
            rank = 1

            for row in table.find_all("tr"):
                if row.find("td", class_="standingsHdTeam"):
                    continue

                team_cell = row.find("td", class_="standingsTeam")
                win_cell = row.find("td", class_="standingsWin")
                loss_cell = row.find("td", class_="standingsLose")
                draw_cell = row.find("td", class_="standingsTai")
                pct_cell = row.find("td", class_="standingsPct")
                gb_cell = row.find("td", class_="standingsGb")

                if not all([team_cell, win_cell, loss_cell, draw_cell, pct_cell, gb_cell]):
                    continue

                team_name = TeamParser._normalize_team_name(team_cell.get_text(" ", strip=True))
                wins = TeamParser._parse_int(win_cell.get_text(strip=True))
                losses = TeamParser._parse_int(loss_cell.get_text(strip=True))
                draws = TeamParser._parse_int(draw_cell.get_text(strip=True))

                if not team_name:
                    continue

                records.append(
                    {
                        "year": year,
                        "league": league,
                        "rank": rank,
                        "team_name": team_name,
                        "games": wins + losses + draws,
                        "wins": wins,
                        "losses": losses,
                        "draws": draws,
                        "win_pct": TeamParser._parse_float(pct_cell.get_text(strip=True)),
                        "games_back": TeamParser._parse_games_back(gb_cell.get_text(strip=True)),
                    }
                )
                rank += 1

        return records

    @staticmethod
    def _parse_float(value: Any) -> float:
        """Parse value as float."""
        try:
            val_str = str(value).strip()
            val_str = val_str.replace(',', '')
            if not val_str:
                return 0.0
            if val_str.startswith("."):
                val_str = f"0{val_str}"
            return float(val_str)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def _parse_int(value: Any) -> int:
        """Parse value as integer."""
        try:
            value_str = str(value).strip()
            if not value_str:
                return 0
            return int(float(value_str))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _parse_games_back(value: Any) -> float:
        value_str = str(value).strip()
        if value_str in {"", "--", "-", "0"}:
            return 0.0
        return TeamParser._parse_float(value_str)

    @staticmethod
    def _normalize_team_name(value: str) -> str:
        return re.sub(r"\s+", "", value.replace("\u3000", " ")).strip()

    @staticmethod
    def _league_from_table(table) -> str:
        header = table.find("td", class_=re.compile(r"standingsHead"))
        header_text = TeamParser._normalize_team_name(header.get_text(" ", strip=True) if header else "")
        if "セントラル" in header_text:
            return "central"
        if "パシフィック" in header_text:
            return "pacific"
        return ""
