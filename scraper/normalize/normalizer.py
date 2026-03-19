"""Normalizes raw scraped data to standardized format."""

import logging
import json
from typing import List, Dict, Any
from pathlib import Path
from hashlib import md5

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalizes raw scraped data."""

    def __init__(self):
        self.processed_records = []

    def normalize_batting_data(
        self,
        raw_batting_records: List[Dict[str, Any]],
        year: int
    ) -> List[Dict[str, Any]]:
        """
        Normalize raw batting data.

        Args:
            raw_batting_records: Raw batting records from parser
            year: Year

        Returns:
            Normalized batting records
        """
        normalized = []

        for record in raw_batting_records:
            try:
                normalized_record = {
                    'type': 'batter',
                    'year': year,
                    'player_id': self._generate_player_id(
                        record['player_name'],
                        year,
                        record['team_code']
                    ),
                    'player_name': record['player_name'],
                    'team_code': record['team_code'],
                    'stats': {
                        'games': int(record.get('games', 0)),
                        'plate_appearances': int(record.get('plate_appearances', 0)),
                        'at_bats': int(record.get('at_bats', 0)),
                        'hits': int(record.get('hits', 0)),
                        'doubles': int(record.get('doubles', 0)),
                        'triples': int(record.get('triples', 0)),
                        'home_runs': int(record.get('home_runs', 0)),
                        'rbi': int(record.get('rbi', 0)),
                        'runs': int(record.get('runs', 0)),
                        'strikeouts': int(record.get('strikeouts', 0)),
                        'walks': int(record.get('walks', 0)),
                        'hit_by_pitch': int(record.get('hit_by_pitch', 0)),
                        'stolen_bases': int(record.get('stolen_bases', 0)),
                        'batting_avg': float(record.get('batting_avg', 0)),
                        'obp': float(record.get('obp', 0)),
                        'slugging_pct': float(record.get('slugging_pct', 0)),
                        'ops': float(record.get('ops', 0)),
                    }
                }
                normalized.append(normalized_record)
            except Exception as e:
                logger.error(f"Error normalizing batting record: {e}")
                continue

        return normalized

    def normalize_pitching_data(
        self,
        raw_pitching_records: List[Dict[str, Any]],
        year: int
    ) -> List[Dict[str, Any]]:
        """
        Normalize raw pitching data.

        Args:
            raw_pitching_records: Raw pitching records from parser
            year: Year

        Returns:
            Normalized pitching records
        """
        normalized = []

        for record in raw_pitching_records:
            try:
                normalized_record = {
                    'type': 'pitcher',
                    'year': year,
                    'player_id': self._generate_player_id(
                        record['player_name'],
                        year,
                        record['team_code']
                    ),
                    'player_name': record['player_name'],
                    'team_code': record['team_code'],
                    'stats': {
                        'appearances': int(record.get('appearances', 0)),
                        'starts': int(record.get('starts', 0)),
                        'wins': int(record.get('wins', 0)),
                        'losses': int(record.get('losses', 0)),
                        'saves': int(record.get('saves', 0)),
                        'holds': int(record.get('holds', 0)),
                        'innings_pitched': float(record.get('innings_pitched', 0)),
                        'hits_allowed': int(record.get('hits_allowed', 0)),
                        'home_runs_allowed': int(record.get('home_runs_allowed', 0)),
                        'strikeouts': int(record.get('strikeouts', 0)),
                        'walks': int(record.get('walks', 0)),
                        'runs_allowed': int(record.get('runs_allowed', 0)),
                        'earned_runs': int(record.get('earned_runs', 0)),
                        'era': float(record.get('era', 0)),
                        'whip': float(record.get('whip', 0)),
                    }
                }
                normalized.append(normalized_record)
            except Exception as e:
                logger.error(f"Error normalizing pitching record: {e}")
                continue

        return normalized

    def normalize_team_data(
        self,
        raw_team_records: List[Dict[str, Any]],
        year: int
    ) -> List[Dict[str, Any]]:
        """
        Normalize raw team data.

        Args:
            raw_team_records: Raw team records from parser
            year: Year

        Returns:
            Normalized team records
        """
        normalized = []

        for record in raw_team_records:
            try:
                normalized_record = {
                    'type': 'team',
                    'year': year,
                    'team_name': record['team_name'],
                    'stats': {
                        'rank': int(record.get('rank', 0)),
                        'games': int(record.get('games', 0)),
                        'wins': int(record.get('wins', 0)),
                        'losses': int(record.get('losses', 0)),
                        'draws': int(record.get('draws', 0)),
                        'win_pct': float(record.get('win_pct', 0)),
                        'games_back': float(record.get('games_back', 0)),
                    }
                }
                normalized.append(normalized_record)
            except Exception as e:
                logger.error(f"Error normalizing team record: {e}")
                continue

        return normalized

    def save_normalized_data(
        self,
        normalized_records: List[Dict[str, Any]],
        output_path: Path
    ) -> None:
        """
        Save normalized data to JSON file.

        Args:
            normalized_records: Normalized records
            output_path: Path to save JSON file
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(normalized_records, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved normalized data to {output_path}")
        except Exception as e:
            logger.error(f"Error saving normalized data: {e}")

    @staticmethod
    def _generate_player_id(
        player_name: str,
        year: int,
        team_code: str
    ) -> str:
        """
        Generate a consistent player ID from name, year, and team.

        Args:
            player_name: Player name
            year: Year
            team_code: Team code

        Returns:
            Player ID string
        """
        # Use MD5 hash of name + team + first occurrence year
        # This creates a stable ID that will be consistent across years
        identifier = f"{player_name}_{team_code}"
        player_hash = md5(identifier.encode()).hexdigest()[:8]
        return f"{player_hash}_{year}"
