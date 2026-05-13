from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.crud import product as crud_product
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.services.forecasting.engine import ForecastingEngine
from app.core.cache import get_cached_forecast, set_cached_forecast, build_forecast_key
from app.core.limiter import limiter

router = APIRouter()
engine = ForecastingEngine()


@router.post(
    "/{product_id}",
    response_model=ForecastResponse,
    summary="Generate demand forecast",
    description="""
    Generates a demand forecast for a product using automated model selection.

    The engine runs the following pipeline:
    1. Loads sales history from DB (fills missing days with 0)
    2. Detects trend (R² threshold 0.25), seasonality (CV threshold 0.15), and volatility
    3. Selects candidate models based on detected factors
    4. Backtests all candidates using MAE — picks the winner
    5. Generates forecast with safety stock recommendation

    Results are cached in Redis for 5 minutes. Returns 422 if insufficient history (< 14 days).
    """
)
@limiter.limit("10/minute")
def generate_forecast(
    request: Request,
    product_id: UUID,
    forecast_in: ForecastRequest,
    db: Session = Depends(get_db)
):
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    key = build_forecast_key(str(product_id), forecast_in.horizon_days, forecast_in.history_days)
    cached = get_cached_forecast(key)
    if cached:
        return ForecastResponse(**cached)

    try:
        report = engine.generate(
            db=db,
            product_id=product_id,
            horizon_days=forecast_in.horizon_days,
            history_days=forecast_in.history_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    response = ForecastResponse(**report.__dict__)
    set_cached_forecast(key, response.model_dump())
    return response