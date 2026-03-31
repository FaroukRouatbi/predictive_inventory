from dataclasses import dataclass


@dataclass
class TrendAnalysis:
    has_trend: bool
    direction: str        # "upward" / "downward" / "flat"
    slope: float          # units per day
    strength: float       # R² value 0.0 → 1.0


def detect_trend(daily_sales: list[float], min_r_squared: float = 0.25) -> TrendAnalysis:
    """
    Fits a linear regression line through the sales data and
    measures how well it fits (R²).

    R² (R-squared) answers: "how much of the variation in sales
    is explained by a straight line trend?"

    R² = 0.0 → data is pure noise, no trend whatsoever
    R² = 1.0 → data follows a perfect straight line
    R² > 0.25 → meaningful trend worth modeling (our threshold)
    """
    n = len(daily_sales)

    if n < 7:
        return TrendAnalysis(
            has_trend=False,
            direction="flat",
            slope=0.0,
            strength=0.0
        )

    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(daily_sales) / n

    # Calculate slope and intercept (same least squares as LinearTrendModel)
    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, daily_sales))
    denominator = sum((xi - x_mean) ** 2 for xi in x)

    if denominator == 0:
        return TrendAnalysis(has_trend=False, direction="flat", slope=0.0, strength=0.0)

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    # Calculate R² — how well does the line fit?
    ss_res = sum((yi - (intercept + slope * xi)) ** 2 for xi, yi in zip(x, daily_sales))
    ss_tot = sum((yi - y_mean) ** 2 for yi in daily_sales)

    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    has_trend = r_squared >= min_r_squared and abs(slope) > 0.05

    if not has_trend:
        direction = "flat"
    elif slope > 0:
        direction = "upward"
    else:
        direction = "downward"

    return TrendAnalysis(
        has_trend=has_trend,
        direction=direction,
        slope=round(slope, 4),
        strength=round(r_squared, 4)
    )