"""Parser for individual NPB player pages."""

import logging
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PlayerParser:
    """Parses individual player pages from NPB HTML."""

    @staticmethod
    def parse_player_page(html: str, npb_player_id: str) -> Optional[Dict[str, Any]]:
        """
        Parse individual player page.

        Args:
            html: HTML content
            npb_player_id: NPB player ID

        Returns:
            Dictionary with player information or None
        """
        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Extract player info from page structure
            player_info = {
                'npb_player_id': npb_player_id,
                'name_ja': None,
                'name_en': None,
                'position': None,
                'team': None,
                'jersey_number': None,
                'birth_date': None,
                'height': None,
                'weight': None,
                'throws': None,
                'bats': None,
            }

            # Try to extract player name from page title or header
            title = soup.find('title')
            if title:
                title_text = title.string or ''
                # Assume format like "選手名 - NPB"
                name = title_text.split(' - ')[0].strip()
                if name:
                    player_info['name_ja'] = name

            # Try to find player header/info section
            header = soup.find('div', {'class': re.compile('player.*info', re.I)})
            if not header:
                header = soup.find('div', {'class': 'profile'})
            if not header:
                header = soup.find('table')

            if header:
                # Extract basic info from header
                text = header.get_text()

                # Try to extract position
                pos_match = re.search(r'ポジション[:：]\s*(.+?)(?:\n|$)', text)
                if pos_match:
                    player_info['position'] = pos_match.group(1).strip()

                # Try to extract team
                team_match = re.search(r'所属球団[:：]\s*(.+?)(?:\n|$)', text)
                if team_match:
                    player_info['team'] = team_match.group(1).strip()

                # Try to extract jersey number
                number_match = re.search(r'背番号[:：]\s*(\d+)', text)
                if number_match:
                    player_info['jersey_number'] = int(number_match.group(1))

                # Try to extract birth date
                birth_match = re.search(r'生年月日[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日)', text)
                if birth_match:
                    player_info['birth_date'] = birth_match.group(1)

                # Try to extract physical stats
                height_match = re.search(r'身長[:：]\s*(\d+)cm', text)
                if height_match:
                    player_info['height'] = int(height_match.group(1))

                weight_match = re.search(r'体重[:：]\s*(\d+)kg', text)
                if weight_match:
                    player_info['weight'] = int(weight_match.group(1))

                # Try to extract throwing hand
                throws_match = re.search(r'投：\s*(\S+)', text)
                if throws_match:
                    throws_text = throws_match.group(1)
                    if '右' in throws_text:
                        player_info['throws'] = 'R'
                    elif '左' in throws_text:
                        player_info['throws'] = 'L'

                # Try to extract batting hand
                bats_match = re.search(r'打：\s*(\S+)', text)
                if bats_match:
                    bats_text = bats_match.group(1)
                    if '右' in bats_text:
                        player_info['bats'] = 'R'
                    elif '左' in bats_text:
                        player_info['bats'] = 'L'

            return player_info if player_info['name_ja'] else None
        except Exception as e:
            logger.error(f"Error parsing player page {npb_player_id}: {e}")
            return None

    @staticmethod
    def parse_player_pages(html_dict: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Parse multiple player pages.

        Args:
            html_dict: Dictionary with player IDs as keys and HTML as values

        Returns:
            Dictionary with player IDs as keys and player info dicts as values
        """
        results = {}
        for player_id, html in html_dict.items():
            player_info = PlayerParser.parse_player_page(html, player_id)
            if player_info:
                results[player_id] = player_info

        return results
