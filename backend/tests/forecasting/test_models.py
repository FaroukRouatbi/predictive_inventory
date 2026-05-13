from app.services.forecasting.models.moving_average import SimpleMovingAverage
from app.services.forecasting.models.weighted_average import WeightedMovingAverage
from app.services.forecasting.models.linear_trend import LinearTrendModel
from app.services.forecasting.models.seasonal import SeasonalModel
from app.services.forecasting.models.base import ForecastInput


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_stable_data():
    """Flat sales around 10 units/day — no trend, no seasonality."""
    return [10.0] * 60


def make_trending_data():
    """Clear upward trend — 1 unit growth per day."""
    return [float(i) for i in range(1, 61)]


def make_seasonal_data():
    """Weekly cycle — spikes every 7th day."""
    data = []
    for i in range(60):
        data.append(20.0 if i % 7 == 6 else 5.0)
    return data


def make_input(data, horizon=14):
    return ForecastInput(daily_sales=data, horizon_days=horizon)


# ── Simple Moving Average ─────────────────────────────────────────────────────

def test_sma_returns_correct_structure():
    model = SimpleMovingAverage(window=14)
    result = model.fit(make_input(make_stable_data()))
    assert result.model_name == "simple_moving_average"
    assert result.predicted_total > 0
    assert len(result.daily_predictions) == 14
    assert result.mae >= 0
    assert result.confidence in ["high", "medium", "low"]


def test_sma_flat_data_predicts_average():
    model = SimpleMovingAverage(window=14)
    result = model.fit(make_input(make_stable_data()))
    # All predictions should be ~10.0
    for pred in result.daily_predictions:
        assert abs(pred - 10.0) < 0.01


def test_sma_backtest_returns_float():
    model = SimpleMovingAverage(window=14)
    mae = model.backtest(make_stable_data())
    assert isinstance(mae, float)
    assert mae >= 0


# ── Weighted Moving Average ───────────────────────────────────────────────────

def test_wma_returns_correct_structure():
    model = WeightedMovingAverage(window=14)
    result = model.fit(make_input(make_stable_data()))
    assert result.model_name == "weighted_moving_average"
    assert len(result.daily_predictions) == 14
    assert result.mae >= 0


def test_wma_weights_recent_data_more():
    """
    On trending data WMA should predict higher than SMA
    because it weights recent (higher) values more.
    """
    data = make_trending_data()
    sma = SimpleMovingAverage(window=14).fit(make_input(data))
    wma = WeightedMovingAverage(window=14).fit(make_input(data))
    assert wma.predicted_total >= sma.predicted_total


# ── Linear Trend ──────────────────────────────────────────────────────────────

def test_linear_trend_returns_correct_structure():
    model = LinearTrendModel()
    result = model.fit(make_input(make_trending_data()))
    assert result.model_name == "linear_trend"
    assert len(result.daily_predictions) == 14
    assert result.predicted_total > 0


def test_linear_trend_predicts_growth():
    """On clearly trending data predictions should increase over time."""
    model = LinearTrendModel()
    result = model.fit(make_input(make_trending_data()))
    # Last prediction should be higher than first
    assert result.daily_predictions[-1] > result.daily_predictions[0]


def test_linear_trend_insufficient_data():
    """Falls back gracefully when not enough data."""
    model = LinearTrendModel()
    result = model.fit(make_input([10.0] * 5))
    assert result.confidence == "low"


# ── Seasonal Model ────────────────────────────────────────────────────────────

def test_seasonal_returns_correct_structure():
    model = SeasonalModel(period=7)
    result = model.fit(make_input(make_seasonal_data()))
    assert result.model_name == "seasonal"
    assert len(result.daily_predictions) == 14
    assert result.predicted_total > 0


def test_seasonal_detects_weekly_pattern():
    """
    On data with a clear weekly spike the seasonal model
    should produce varying daily predictions, not flat ones.
    """
    model = SeasonalModel(period=7)
    result = model.fit(make_input(make_seasonal_data()))
    # Predictions should vary — not all the same value
    assert len(set(result.daily_predictions)) > 1


def test_seasonal_insufficient_data():
    """Falls back gracefully when not enough data."""
    model = SeasonalModel(period=7)
    result = model.fit(make_input([10.0] * 10))
    assert result.confidence == "low"