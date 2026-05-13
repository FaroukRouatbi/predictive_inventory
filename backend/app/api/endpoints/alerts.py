from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.reorder_alert import ReorderAlertResponse, ResolveAlertRequest
from app.crud import reorder_alert as crud_alert
from app.crud import product as crud_product
from app.core.limiter import limiter
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get(
    "/",
    response_model=List[ReorderAlertResponse],
    summary="Get active reorder alerts",
    description="Returns all unresolved reorder alerts across all products."
)
@limiter.limit("60/minute")
def read_unresolved_alerts(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_alert.get_unresolved_alerts(db=db, skip=skip, limit=limit)


@router.get(
    "/all",
    response_model=List[ReorderAlertResponse],
    summary="Get all alerts including resolved",
    description="Returns all alerts including resolved ones."
)
@limiter.limit("60/minute")
def read_all_alerts(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_alert.get_all_alerts(db=db, skip=skip, limit=limit)


@router.get(
    "/product/{product_id}",
    response_model=List[ReorderAlertResponse],
    summary="Get alerts for a product",
    description="Returns all alerts for a specific product."
)
@limiter.limit("60/minute")
def read_alerts_by_product(
    request: Request,
    product_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return crud_alert.get_alerts_by_product(db=db, product_id=product_id, skip=skip, limit=limit)


@router.get(
    "/{alert_id}",
    response_model=ReorderAlertResponse,
    summary="Get an alert by ID",
    description="Returns a single reorder alert by its UUID."
)
@limiter.limit("60/minute")
def read_alert(
    request: Request,
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = crud_alert.get_alert(db=db, alert_id=alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return alert


@router.put(
    "/{alert_id}/resolve",
    response_model=ReorderAlertResponse,
    summary="Resolve a reorder alert",
    description="Marks an alert as resolved."
)
@limiter.limit("30/minute")
def resolve_alert(
    request: Request,
    alert_id: UUID,
    resolve_in: ResolveAlertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = crud_alert.resolve_alert(db=db, alert_id=alert_id, notes=resolve_in.notes)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return alert


@router.put(
    "/{alert_id}/unresolve",
    response_model=ReorderAlertResponse,
    summary="Revert a resolved alert",
    description="Reverts a resolved alert back to unresolved."
)
@limiter.limit("30/minute")
def unresolve_alert(
    request: Request,
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = crud_alert.unresolve_alert(db=db, alert_id=alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    return alert