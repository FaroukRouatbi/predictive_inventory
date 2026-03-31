from app.services.forecasting.models.base import BaseForecastModel, ForecastInput, ForecastResult


class LinearTrendModel(BaseForecastModel):
    """
    Fits a straight line through historical sales data and
    projects it forward. Best for products with consistent
    growth or decline over time.
    Example: Protein Powder — steadily growing sales.
    """

    def _fit_linear(self, values: list[float]) -> tuple[float, float]:
        """
        Calculates slope and intercept using least squares regression.
        This is the math behind drawing the best-fit line through data.

        Returns (slope, intercept) where:
        - slope     → how much sales change per day
        - intercept → starting point of the line
        """
        n = len(values)
        x = list(range(n))

        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
        denominator = sum((xi - x_mean) ** 2 for xi in x)

        if denominator == 0:
            return 0.0, y_mean

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        return slope, intercept

    def fit(self, input_data: ForecastInput) -> ForecastResult:
        daily_sales = input_data.daily_sales
        horizon = input_data.horizon_days

        if len(daily_sales) < 7:
            # Not enough data for meaningful trend detection
            avg = sum(daily_sales) / len(daily_sales)
            daily_predictions = [round(avg, 2)] * horizon
            return ForecastResult(
                model_name="linear_trend",
                predicted_total=round(avg * horizon, 2),
                daily_predictions=daily_predictions,
                mae=float("inf"),
                confidence="low",
                notes="Insufficient data for trend analysis. Fell back to simple average."
            )

        slope, intercept = self._fit_linear(daily_sales)
        n = len(daily_sales)

        # Project the line forward from the end of the history
        daily_predictions = []
        for i in range(horizon):
            predicted_day = intercept + slope * (n + i)
            daily_predictions.append(round(max(0, predicted_day), 2))

        predicted_total = round(sum(daily_predictions), 2)

        mae = self.backtest(daily_sales)
        avg_sales = sum(daily_sales) / len(daily_sales) if daily_sales else 0
        confidence = self._confidence_from_mae(mae, avg_sales)

        direction = "upward" if slope > 0.1 else "downward" if slope < -0.1 else "flat"

        return ForecastResult(
            model_name="linear_trend",
            predicted_total=predicted_total,
            daily_predictions=daily_predictions,
            mae=mae,
            confidence=confidence,
            notes=f"Trend direction: {direction}. Slope: {round(slope, 3)} units/day."
        )

    def backtest(self, daily_sales: list[float], test_window: int = 14) -> float:
        if len(daily_sales) < 21:
            return float("inf")

        train = daily_sales[:-test_window]
        actual = daily_sales[-test_window:]

        slope, intercept = self._fit_linear(train)
        n = len(train)

        predicted = []
        for i in range(test_window):
            val = intercept + slope * (n + i)
            predicted.append(max(0, val))

        return self._calculate_mae(actual, predicted)