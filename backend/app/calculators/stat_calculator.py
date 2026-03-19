from typing import Optional


class StatCalculator:
    """Calculator for derived statistics."""

    @staticmethod
    def batting_average(hits: Optional[int], at_bats: Optional[int]) -> Optional[float]:
        """Calculate batting average (H / AB)."""
        if not hits or not at_bats or at_bats == 0:
            return None
        return round(hits / at_bats, 3)

    @staticmethod
    def on_base_percentage(
        hits: Optional[int],
        walks: Optional[int],
        hit_by_pitch: Optional[int],
        plate_appearances: Optional[int],
    ) -> Optional[float]:
        """Calculate on-base percentage (H + W + HBP) / PA."""
        if (
            not plate_appearances
            or plate_appearances == 0
            or (hits is None and walks is None and hit_by_pitch is None)
        ):
            return None

        h = hits or 0
        w = walks or 0
        hbp = hit_by_pitch or 0
        return round((h + w + hbp) / plate_appearances, 3)

    @staticmethod
    def slugging_percentage(
        hits: Optional[int],
        doubles: Optional[int],
        triples: Optional[int],
        home_runs: Optional[int],
        at_bats: Optional[int],
    ) -> Optional[float]:
        """Calculate slugging percentage (TB / AB)."""
        if not at_bats or at_bats == 0:
            return None

        h = hits or 0
        d = doubles or 0
        t = triples or 0
        hr = home_runs or 0

        total_bases = h + (d * 2) + (t * 3) + (hr * 4) - (d + t + hr)
        return round(total_bases / at_bats, 3)

    @staticmethod
    def ops(
        on_base_pct: Optional[float], slugging_pct: Optional[float]
    ) -> Optional[float]:
        """Calculate OPS (OBP + SLG)."""
        if not on_base_pct or not slugging_pct:
            return None
        return round(on_base_pct + slugging_pct, 3)

    @staticmethod
    def era(
        earned_runs: Optional[int], innings_pitched: Optional[float]
    ) -> Optional[float]:
        """Calculate ERA (ER * 9 / IP)."""
        if not earned_runs or not innings_pitched or innings_pitched == 0:
            return None
        return round((earned_runs * 9) / innings_pitched, 2)

    @staticmethod
    def whip(
        walks_allowed: Optional[int],
        hits_allowed: Optional[int],
        innings_pitched: Optional[float],
    ) -> Optional[float]:
        """Calculate WHIP ((W + H) / IP)."""
        if not innings_pitched or innings_pitched == 0:
            return None

        w = walks_allowed or 0
        h = hits_allowed or 0
        return round((w + h) / innings_pitched, 2)

    @staticmethod
    def winning_percentage(
        wins: Optional[int], losses: Optional[int]
    ) -> Optional[float]:
        """Calculate winning percentage (W / (W + L))."""
        if not wins or not losses:
            return None

        total = wins + losses
        if total == 0:
            return None
        return round(wins / total, 3)

    @staticmethod
    def team_batting_average(
        hits: Optional[int], at_bats: Optional[int]
    ) -> Optional[float]:
        """Calculate team batting average."""
        if not hits or not at_bats or at_bats == 0:
            return None
        return round(hits / at_bats, 3)

    @staticmethod
    def team_era(
        earned_runs: Optional[int], innings_pitched: Optional[float]
    ) -> Optional[float]:
        """Calculate team ERA."""
        if not earned_runs or not innings_pitched or innings_pitched == 0:
            return None
        return round((earned_runs * 9) / innings_pitched, 2)
