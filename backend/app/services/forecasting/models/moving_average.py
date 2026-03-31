from app.services.forecasting.models.base import BaseForecastModel, ForecastInput, ForecastResult


class SimpleMovingAverage(BaseForecastModel):
    """
    Forecasts demand by averaging the last N days of sales.
    Best for: stable products with no clear trend or seasonality.
    Example: Air Purifier — flat, predictable, low volatility.
    """

    def __init__(self, window: int = 14):
        """
        window → how many recent days to average.
        14 days is a good default — long enough to smooth noise,
        short enough to stay responsive to recent changes.
        """
        self.window = window

    def fit(self, input_data: ForecastInput) -> ForecastResult:
        daily_sales = input_data.daily_sales
        horizon = input_data.horizon_days

        # Need at least enough data to fill the window
        if len(daily_sales) < self.window:
            actual_window = len(daily_sales)
        else:
            actual_window = self.window

        # Average the most recent window of days
        recent = daily_sales[-actual_window:]
        avg = sum(recent) / len(recent)

        # Project that average forward for each day in the horizon
        daily_predictions = [round(avg, 2)] * horizon
        predicted_total = round(avg * horizon, 2)

        # Backtest to get MAE
        mae = self.backtest(daily_sales)
        avg_sales = sum(daily_sales) / len(daily_sales) if daily_sales else 0
        confidence = self._confidence_from_mae(mae, avg_sales)

        return ForecastResult(
            model_name="simple_moving_average",
            predicted_total=predicted_total,
            daily_predictions=daily_predictions,
            mae=mae,
            confidence=confidence,
            notes=f"Averaged last {actual_window} days. Daily avg: {round(avg, 2)} units."
        )

    def backtest(self, daily_sales: list[float], test_window: int = 14) -> float:
        """
        Hides the last `test_window` days, forecasts them using
        the preceding data, then measures MAE against reality.
        """
        if len(daily_sales) < self.window + test_window:
            return float("inf")

        # Split into training data and holdout (hidden) data
        train = daily_sales[:-test_window]
        actual = daily_sales[-test_window:]

        # Forecast using training data only
        recent = train[-self.window:]
        avg = sum(recent) / len(recent)
        predicted = [avg] * test_window

        return self._calculate_mae(actual, predicted)