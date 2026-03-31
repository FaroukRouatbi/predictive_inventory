from app.services.forecasting.models.base import BaseForecastModel, ForecastInput, ForecastResult


class SeasonalModel(BaseForecastModel):
    """
    Detects repeating weekly patterns in sales data and uses
    them to forecast. Best for products that sell differently
    on different days of the week.
    Example: Winter Jacket — spikes on weekends.
    """

    def __init__(self, period: int = 7):
        """
        period → length of the seasonal cycle in days.
        7 = weekly cycle (default and most common for retail).
        """
        self.period = period

    def _calculate_seasonal_indices(self, values: list[float]) -> list[float]:
        """
        Calculates how much each day of the cycle deviates
        from the overall average.

        Example result: [0.8, 0.9, 1.0, 1.0, 1.1, 1.5, 1.4]
        → day 6 sells 50% more than average (weekend spike)
        → day 0 sells 20% less than average (Monday dip)
        """
        overall_avg = sum(values) / len(values)
        if overall_avg == 0:
            return [1.0] * self.period

        # Group values by their position in the cycle
        buckets = [[] for _ in range(self.period)]
        for i, val in enumerate(values):
            buckets[i % self.period].append(val)

        # Calculate each day's average as a ratio to the overall average
        indices = []
        for bucket in buckets:
            if bucket:
                day_avg = sum(bucket) / len(bucket)
                indices.append(day_avg / overall_avg)
            else:
                indices.append(1.0)

        return indices

    def fit(self, input_data: ForecastInput) -> ForecastResult:
        daily_sales = input_data.daily_sales
        horizon = input_data.horizon_days

        if len(daily_sales) < self.period * 2:
            avg = sum(daily_sales) / len(daily_sales)
            daily_predictions = [round(avg, 2)] * horizon
            return ForecastResult(
                model_name="seasonal",
                predicted_total=round(avg * horizon, 2),
                daily_predictions=daily_predictions,
                mae=float("inf"),
                confidence="low",
                notes="Insufficient data to detect seasonal pattern."
            )

        overall_avg = sum(daily_sales) / len(daily_sales)
        indices = self._calculate_seasonal_indices(daily_sales)
        n = len(daily_sales)

        # Apply seasonal indices to project forward
        daily_predictions = []
        for i in range(horizon):
            cycle_position = (n + i) % self.period
            predicted_day = overall_avg * indices[cycle_position]
            daily_predictions.append(round(max(0, predicted_day), 2))

        predicted_total = round(sum(daily_predictions), 2)

        mae = self.backtest(daily_sales)
        avg_sales = overall_avg
        confidence = self._confidence_from_mae(mae, avg_sales)

        peak_day = indices.index(max(indices))
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        peak_label = days[peak_day] if self.period == 7 else f"day {peak_day}"

        return ForecastResult(
            model_name="seasonal",
            predicted_total=predicted_total,
            daily_predictions=daily_predictions,
            mae=mae,
            confidence=confidence,
            notes=f"Weekly seasonal pattern detected. Peak day: {peak_label}. "
                  f"Indices: {[round(i, 2) for i in indices]}"
        )

    def backtest(self, daily_sales: list[float], test_window: int = 14) -> float:
        if len(daily_sales) < self.period * 2 + test_window:
            return float("inf")

        train = daily_sales[:-test_window]
        actual = daily_sales[-test_window:]

        overall_avg = sum(train) / len(train)
        indices = self._calculate_seasonal_indices(train)
        n = len(train)

        predicted = []
        for i in range(test_window):
            cycle_position = (n + i) % self.period
            predicted.append(max(0, overall_avg * indices[cycle_position]))

        return self._calculate_mae(actual, predicted)