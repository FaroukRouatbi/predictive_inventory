from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ForecastInput:
    """
    The standardized input every forecasting model receives.
    All models work on the same data structure — no model
    knows or cares where the data came from.
    """
    daily_sales: list[float]      # time-ordered list of daily quantities
    horizon_days: int             # how many days ahead to forecast


@dataclass
class ForecastResult:
    """
    The standardized output every forecasting model returns.
    The engine compares these to pick the best model.
    """
    model_name: str               # e.g. "weighted_moving_average"
    predicted_total: float        # total predicted demand over horizon
    daily_predictions: list[float]# day-by-day breakdown
    mae: float                    # Mean Absolute Error (backtested accuracy)
    confidence: str               # "high" / "medium" / "low"
    notes: Optional[str] = None   # human-readable explanation


class BaseForecastModel(ABC):
    """
    Abstract base class all forecasting models inherit from.
    Enforces a consistent interface so the engine can treat
    all models identically — it just calls .fit() and .backtest()
    on any model without knowing which one it is.
    """

    @abstractmethod
    def fit(self, input_data: ForecastInput) -> ForecastResult:
        """
        Run the forecast. Takes standardized input, returns standardized output.
        Every model must implement this.
        """
        pass

    @abstractmethod
    def backtest(self, daily_sales: list[float], test_window: int = 14) -> float:
        """
        Measure model accuracy by hiding the last `test_window` days,
        forecasting them, then comparing against reality.
        Returns MAE (Mean Absolute Error) — lower is better.
        """
        pass

    def _calculate_mae(
        self,
        actual: list[float],
        predicted: list[float]
    ) -> float:
        """
        Shared MAE calculation available to all models.
        MAE = average of |actual - predicted| per day.
        """
        if not actual or not predicted:
            return float("inf")
        pairs = zip(actual, predicted)
        return sum(abs(a - p) for a, p in pairs) / len(actual)

    def _confidence_from_mae(self, mae: float, avg_sales: float) -> str:
        """
        Converts MAE into a human-readable confidence level.
        Uses MAE as a % of average sales — relative error matters
        more than absolute error.
        """
        if avg_sales == 0:
           return "low"

    # Low volume products — use absolute MAE thresholds
        if avg_sales < 3.0:
            if mae < 1.0:
                return "high"
            elif mae < 2.0:
                return "medium"
            else:
                return "low"

        # Normal volume products — use relative error
        relative_error = mae / avg_sales
        if relative_error < 0.15:
            return "high"
        elif relative_error < 0.35:
            return "medium"
        else:
            return "low"