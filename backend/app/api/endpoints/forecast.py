from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.crud import product as crud_product
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.services.forecasting.engine import ForecastingEngine

router = APIRouter()
engine = ForecastingEngine()


@router.post("/{product_id}", response_model=ForecastResponse)
def generate_forecast(
    product_id: UUID,
    request: ForecastRequest,
    db: Session = Depends(get_db)
):
    # Validate product exists
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    try:
        report = engine.generate(
            db=db,
            product_id=product_id,
            horizon_days=request.horizon_days,
            history_days=request.history_days,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    return ForecastResponse(**report.__dict__)