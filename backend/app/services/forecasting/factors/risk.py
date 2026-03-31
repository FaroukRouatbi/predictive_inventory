from dataclasses import dataclass
import math


@dataclass
class RiskAnalysis:
    risk_score: float       # 0.0 (low risk) → 1.0 (high risk)
    volatility: float       # coefficient of variation of daily sales
    safety_stock: int       # recommended buffer units to hold
    risk_label: str         # "low" / "medium" / "high"


def assess_risk(
    daily_sales: list[float],
    lead_time_days: int = 7,
    service_level: float = 0.95
) -> RiskAnalysis:
    """
    Measures how unpredictable this product's demand is and
    calculates how much safety stock to hold as a buffer.

    Two key concepts:

    1. Volatility (CV) = std_deviation / mean
       → measures relative unpredictability
       → CV 0.2 means sales vary ±20% around the average

    2. Safety Stock = Z × σ × √lead_time
       → industry standard formula
       → Z = service level factor (1.65 for 95% service level)
       → σ = standard deviation of daily demand
       → √lead_time = accounts for uncertainty accumulating over time
       → ensures you can meet demand even in bad stretches
    """
    n = len(daily_sales)

    if n < 7:
        return RiskAnalysis(
            risk_score=0.5,
            volatility=0.5,
            safety_stock=10,
            risk_label="medium"
        )

    mean = sum(daily_sales) / n
    if mean == 0:
        return RiskAnalysis(
            risk_score=0.0,
            volatility=0.0,
            safety_stock=0,
            risk_label="low"
        )

    # Standard deviation of daily sales
    variance = sum((x - mean) ** 2 for x in daily_sales) / n
    std_dev = math.sqrt(variance)

    # Coefficient of variation — relative volatility
    cv = std_dev / mean

    # Safety stock using the industry standard formula
    # Z = 1.645 for 95% service level (from normal distribution table)
    z_score = _get_z_score(service_level)
    safety_stock = int(math.ceil(z_score * std_dev * math.sqrt(lead_time_days)))

    # Normalize CV to a 0-1 risk score (cap at CV=1.0 for scoring)
    risk_score = round(min(cv, 1.0), 4)

    if cv < 0.2:
        risk_label = "low"
    elif cv < 0.5:
        risk_label = "medium"
    else:
        risk_label = "high"

    return RiskAnalysis(
        risk_score=risk_score,
        volatility=round(cv, 4),
        safety_stock=safety_stock,
        risk_label=risk_label
    )


def _get_z_score(service_level: float) -> float:
    """
    Returns the Z-score for common service levels.
    These come from the standard normal distribution table.
    """
    z_scores = {
        0.90: 1.282,
        0.95: 1.645,
        0.99: 2.326,
    }
    # Find the closest service level
    closest = min(z_scores.keys(), key=lambda k: abs(k - service_level))
    return z_scores[closest]
