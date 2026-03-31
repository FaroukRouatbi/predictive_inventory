from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.sales_record import get_daily_sales_aggregates
from app.crud.inventory import get_inventory_by_product
from app.services.forecasting.factors.trend import detect_trend, TrendAnalysis
from app.services.forecasting.factors.seasonality import detect_seasonality, SeasonalityAnalysis
from app.services.forecasting.factors.risk import assess_risk, RiskAnalysis
from app.services.forecasting.models.base import ForecastInput, ForecastResult
from app.services.forecasting.models.moving_average import SimpleMovingAverage
from app.services.forecasting.models.weighted_average import WeightedMovingAverage
from app.services.forecasting.models.linear_trend import LinearTrendModel
from app.services.forecasting.models.seasonal import SeasonalModel


# ── Output Schema ─────────────────────────────────────────────────────────────

@dataclass
class ForecastReport:
    """
    The complete forecast output returned to the API endpoint.
    Contains not just the prediction but the full reasoning behind it.
    """
    product_id: str
    forecast_horizon_days: int
    predicted_demand: float
    daily_breakdown: list[float]
    recommended_reorder_quantity: int
    safety_stock: int
    model_used: str
    model_selection_reason: str
    confidence_level: str
    risk_score: float
    risk_label: str
    trend_direction: str
    trend_strength: float
    seasonality_detected: bool
    seasonality_strength: float
    based_on_days_of_history: int
    generated_at: str


# ── Engine ────────────────────────────────────────────────────────────────────

class ForecastingEngine:
    """
    Orchestrates the full forecasting pipeline:

    1. Load sales history from DB
    2. Run factor detectors (trend, seasonality, risk)
    3. Select candidate models based on detected factors
    4. Backtest all candidates and pick the most accurate
    5. Run the winner on the full dataset
    6. Build and return a complete ForecastReport
    """

    # Minimum days of history required to produce a meaningful forecast
    MIN_HISTORY_DAYS = 14

    # All available models — engine will select the best one
    AVAILABLE_MODELS = [
        SimpleMovingAverage(window=14),
        WeightedMovingAverage(window=14),
        LinearTrendModel(),
        SeasonalModel(period=7),
    ]

    def generate(
        self,
        db: Session,
        product_id: UUID,
        horizon_days: int = 30,
        history_days: int = 90,
    ) -> ForecastReport:
        """
        Main entry point. Call this from the forecast endpoint.
        """

        # ── Step 1: Load history ──────────────────────────────────────────────
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=history_days)

        raw = get_daily_sales_aggregates(
            db=db,
            product_id=product_id,
            start_date=start_date,
            end_date=end_date
        )

        # Fill missing days with 0 — gaps mean zero sales that day
        daily_sales = _fill_missing_days(raw, start_date, history_days)

        if len(daily_sales) < self.MIN_HISTORY_DAYS:
            raise ValueError(
                f"Insufficient history. Need at least {self.MIN_HISTORY_DAYS} days, "
                f"got {len(daily_sales)}."
            )

        # ── Step 2: Run factor detectors ──────────────────────────────────────
        trend = detect_trend(daily_sales)
        seasonality = detect_seasonality(daily_sales)
        risk = assess_risk(daily_sales)

        # ── Step 3: Select candidate models ───────────────────────────────────
        candidates = _select_candidates(trend, seasonality)

        # ── Step 4: Backtest candidates, pick winner ───────────────────────────
        best_model, selection_reason = _pick_best_model(candidates, daily_sales)

        # ── Step 5: Run winner on full dataset ────────────────────────────────
        forecast_input = ForecastInput(
            daily_sales=daily_sales,
            horizon_days=horizon_days
        )
        result: ForecastResult = best_model.fit(forecast_input)

        # ── Step 6: Calculate reorder quantity ────────────────────────────────
        reorder_quantity = int(result.predicted_total) + risk.safety_stock

        # ── Step 7: Build report ──────────────────────────────────────────────
        return ForecastReport(
            product_id=str(product_id),
            forecast_horizon_days=horizon_days,
            predicted_demand=round(result.predicted_total, 2),
            daily_breakdown=result.daily_predictions,
            recommended_reorder_quantity=reorder_quantity,
            safety_stock=risk.safety_stock,
            model_used=result.model_name,
            model_selection_reason=selection_reason,
            confidence_level=result.confidence,
            risk_score=risk.risk_score,
            risk_label=risk.risk_label,
            trend_direction=trend.direction,
            trend_strength=trend.strength,
            seasonality_detected=seasonality.has_seasonality,
            seasonality_strength=seasonality.strength,
            based_on_days_of_history=len(daily_sales),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )


# ── Private Helpers ───────────────────────────────────────────────────────────

def _fill_missing_days(
    raw: list[dict],
    start_date: datetime,
    history_days: int
) -> list[float]:
    """
    The DB only returns days where sales occurred.
    Days with no sales are simply absent from the query result.
    This function fills those gaps with 0.0 so every model
    receives a complete, unbroken time series.
    """
    # Build a lookup of date → quantity from DB results
    sales_by_date = {}
    for row in raw:
        date_key = row["date"].date() if hasattr(row["date"], "date") else row["date"]
        sales_by_date[date_key] = float(row["total_quantity"])

    # Walk every day in the window, fill missing with 0
    filled = []
    for i in range(history_days):
        day = (start_date + timedelta(days=i)).date()
        filled.append(sales_by_date.get(day, 0.0))

    return filled


def _select_candidates(
    trend: TrendAnalysis,
    seasonality: SeasonalityAnalysis
) -> list:
    """
    Narrows the model pool based on detected data characteristics.
    The backtester will then pick the best among candidates.

    Logic:
    - Seasonality detected      → SeasonalModel is a strong candidate
    - Trend detected            → LinearTrendModel + WeightedAverage
    - Neither detected          → SimpleMovingAverage + WeightedAverage
    - Always include at least 2 → ensures backtesting has something to compare
    """
    candidates = []

    if seasonality.has_seasonality:
        candidates.append(SeasonalModel(period=seasonality.period))

    if trend.has_trend:
        candidates.append(LinearTrendModel())
        candidates.append(WeightedMovingAverage(window=14))

    if not candidates:
        # Flat, stable product — simple models work best
        candidates.append(SimpleMovingAverage(window=14))
        candidates.append(WeightedMovingAverage(window=14))

    # Always include simple moving average as a baseline fallback
    if not any(isinstance(m, SimpleMovingAverage) for m in candidates):
        candidates.append(SimpleMovingAverage(window=14))

    return candidates


def _pick_best_model(
    candidates: list,
    daily_sales: list[float]
) -> tuple:
    best_model = None
    best_mae = float("inf")
    all_scores = []

    for model in candidates:
        mae = model.backtest(daily_sales)
        all_scores.append((model, mae))

        if mae < best_mae or (          # ← must be INSIDE the for loop
            mae == best_mae and
            isinstance(model, WeightedMovingAverage) and
            not isinstance(best_model, WeightedMovingAverage)
        ):
            best_mae = mae
            best_model = model

    # Fallback — if all backtests failed (insufficient data)
    if best_model is None:
        best_model = SimpleMovingAverage(window=14)
        reason = "Insufficient data for backtesting. Defaulted to simple moving average."
        return best_model, reason

    score_summary = ", ".join(
        f"{m.__class__.__name__}(MAE={round(mae, 2)})"
        for m, mae in all_scores
    )
    reason = (
        f"Selected {best_model.__class__.__name__} with lowest MAE={round(best_mae, 2)}. "
        f"All candidates: [{score_summary}]"
    )

    return best_model, reason