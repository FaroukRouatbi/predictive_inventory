import pytest
from app.services.forecasting.factors.trend import detect_trend
from app.services.forecasting.factors.seasonality import detect_seasonality
from app.services.forecasting.factors.risk import assess_risk


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_flat_data():
    return [10.0] * 90


def make_trending_data():
    return [float(i) for i in range(1, 91)]


def make_seasonal_data():
    data = []
    for i in range(90):
        data.append(20.0 if i % 7 == 6 else 5.0)
    return data


def make_volatile_data():
    import random
    random.seed(42)
    return [random.uniform(1, 50) for _ in range(90)]


# ── Trend Detection ───────────────────────────────────────────────────────────

def test_detect_trend_flat_data():
    result = detect_trend(make_flat_data())
    assert result.has_trend == False
    assert result.direction == "flat"
    assert result.strength >= 0


def test_detect_trend_upward_data():
    result = detect_trend(make_trending_data())
    assert result.has_trend == True
    assert result.direction == "upward"
    assert result.slope > 0
    assert result.strength > 0.25


def test_detect_trend_insufficient_data():
    result = detect_trend([10.0] * 5)
    assert result.has_trend == False
    assert result.direction == "flat"


def test_detect_trend_returns_correct_fields():
    result = detect_trend(make_flat_data())
    assert hasattr(result, "has_trend")
    assert hasattr(result, "direction")
    assert hasattr(result, "slope")
    assert hasattr(result, "strength")


# ── Seasonality Detection ─────────────────────────────────────────────────────

def test_detect_seasonality_flat_data():
    result = detect_seasonality(make_flat_data())
    assert result.has_seasonality == False
    assert result.strength < 0.15


def test_detect_seasonality_seasonal_data():
    result = detect_seasonality(make_seasonal_data())
    assert result.has_seasonality == True
    assert result.strength >= 0.15
    assert result.strength <= 1.0  # capped at 1.0


def test_detect_seasonality_insufficient_data():
    result = detect_seasonality([10.0] * 10)
    assert result.has_seasonality == False


def test_detect_seasonality_returns_correct_fields():
    result = detect_seasonality(make_flat_data())
    assert hasattr(result, "has_seasonality")
    assert hasattr(result, "period")
    assert hasattr(result, "strength")
    assert hasattr(result, "peak_day")
    assert hasattr(result, "indices")


# ── Risk Assessment ───────────────────────────────────────────────────────────

def test_assess_risk_stable_data():
    result = assess_risk(make_flat_data())
    assert result.risk_label == "low"
    assert result.risk_score < 0.2
    assert result.safety_stock >= 0


def test_assess_risk_volatile_data():
    result = assess_risk(make_volatile_data())
    assert result.risk_label in ["medium", "high"]
    assert result.risk_score > 0.2


def test_assess_risk_safety_stock_positive():
    result = assess_risk(make_flat_data())
    assert result.safety_stock >= 0


def test_assess_risk_insufficient_data():
    result = assess_risk([10.0] * 5)
    assert result.risk_label == "medium"
    assert result.safety_stock > 0


def test_assess_risk_returns_correct_fields():
    result = assess_risk(make_flat_data())
    assert hasattr(result, "risk_score")
    assert hasattr(result, "volatility")
    assert hasattr(result, "safety_stock")
    assert hasattr(result, "risk_label")