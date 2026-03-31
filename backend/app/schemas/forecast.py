from pydantic import BaseModel, Field
from typing import Optional


class ForecastRequest(BaseModel):
    horizon_days: int = Field(default=30, ge=7, le=365)
    history_days: int = Field(default=90, ge=14, le=365)


class ForecastResponse(BaseModel):
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