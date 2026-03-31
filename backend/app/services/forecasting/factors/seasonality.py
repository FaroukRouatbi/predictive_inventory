from dataclasses import dataclass
import math


@dataclass
class SeasonalityAnalysis:
    has_seasonality: bool
    period: int             # detected cycle length in days
    strength: float         # 0.0 → 1.0, how strong the pattern is
    peak_day: int           # which day in the cycle peaks
    indices: list[float]    # seasonal multiplier per day in cycle


def detect_seasonality(
    daily_sales: list[float],
    period: int = 7,
    min_strength: float = 0.15
) -> SeasonalityAnalysis:
    """
    Measures whether sales follow a repeating cycle of `period` days.

    Strength is measured as the coefficient of variation (CV) of the
    seasonal indices — how much the daily multipliers deviate from 1.0.

    CV = std_deviation / mean of seasonal indices
    CV close to 0   → all days sell roughly the same → no seasonality
    CV above 0.15   → meaningful day-to-day variation → seasonality exists
    """
    n = len(daily_sales)

    if n < period * 2:
        return SeasonalityAnalysis(
            has_seasonality=False,
            period=period,
            strength=0.0,
            peak_day=0,
            indices=[1.0] * period
        )

    overall_avg = sum(daily_sales) / n
    if overall_avg == 0:
        return SeasonalityAnalysis(
            has_seasonality=False,
            period=period,
            strength=0.0,
            peak_day=0,
            indices=[1.0] * period
        )

    # Group sales by position in the cycle
    buckets = [[] for _ in range(period)]
    for i, val in enumerate(daily_sales):
        buckets[i % period].append(val)

    # Calculate seasonal index for each day in the cycle
    indices = []
    for bucket in buckets:
        day_avg = sum(bucket) / len(bucket) if bucket else overall_avg
        indices.append(day_avg / overall_avg)

    # Measure strength via coefficient of variation of indices
    indices_mean = sum(indices) / len(indices)
    variance = sum((idx - indices_mean) ** 2 for idx in indices) / len(indices)
    std_dev = math.sqrt(variance)
    strength = std_dev / indices_mean if indices_mean > 0 else 0.0

    strength = std_dev / indices_mean if indices_mean > 0 else 0.0
    strength = min(strength, 1.0)  # ← add this line

    has_seasonality = strength >= min_strength
    peak_day = indices.index(max(indices))

    return SeasonalityAnalysis(
        has_seasonality=has_seasonality,
        period=period,
        strength=round(strength, 4),
        peak_day=peak_day,
        indices=[round(i, 4) for i in indices]
    )