from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.crud import product as crud_product
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.services.forecasting.engine import ForecastingEngine

from app.core.cache import get_cached_forecast, set_cached_forecast, build_forecast_key
from app.main import limiter

router = APIRouter()
engine = ForecastingEngine()


@router.post("/{product_id}", response_model=ForecastResponse)
@limiter.limit("10/minute")
def generate_forecast(
    request: Request,
    product_id: UUID,
    forecast_in: ForecastRequest,
    db: Session = Depends(get_db)
):
    # Validate product exists
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

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
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    response = ForecastResponse(**report.__dict__)
    set_cached_forecast(key, response.model_dump())

    return response