from app.services.forecasting.models.base import BaseForecastModel, ForecastInput, ForecastResult


class WeightedMovingAverage(BaseForecastModel):
    """
    Like simple moving average but more recent days carry more weight.
    Best for: products with a gradual trend — recent sales are
    more predictive of the future than older ones.
    Example: Wireless Headphones — stable but slightly trending up.
    """

    def __init__(self, window: int = 14):
        self.window = window

    def _weighted_average(self, values: list[float]) -> float:
        """
        Assigns linearly increasing weights to values.
        Most recent value gets weight N, oldest gets weight 1.

        Example with 3 values [a, b, c]:
        weights = [1, 2, 3]
        result  = (1*a + 2*b + 3*c) / (1+2+3)
        """
        n = len(values)
        weights = list(range(1, n + 1))  # [1, 2, 3, ... n]
        weighted_sum = sum(w * v for w, v in zip(weights, values))
        return weighted_sum / sum(weights)

    def fit(self, input_data: ForecastInput) -> ForecastResult:
        daily_sales = input_data.daily_sales
        horizon = input_data.horizon_days

        actual_window = min(self.window, len(daily_sales))
        recent = daily_sales[-actual_window:]
        avg = self._weighted_average(recent)

        daily_predictions = [round(avg, 2)] * horizon
        predicted_total = round(avg * horizon, 2)

        mae = self.backtest(daily_sales)
        avg_sales = sum(daily_sales) / len(daily_sales) if daily_sales else 0
        confidence = self._confidence_from_mae(mae, avg_sales)

        return ForecastResult(
            model_name="weighted_moving_average",
            predicted_total=predicted_total,
            daily_predictions=daily_predictions,
            mae=mae,
            confidence=confidence,
            notes=f"Weighted average of last {actual_window} days. Recent days weighted higher."
        )

    def backtest(self, daily_sales: list[float], test_window: int = 14) -> float:
        if len(daily_sales) < self.window + test_window:
            return float("inf")

        train = daily_sales[:-test_window]
        actual = daily_sales[-test_window:]

        recent = train[-self.window:]
        avg = self._weighted_average(recent)
        predicted = [avg] * test_window

        return self._calculate_mae(actual, predicted)