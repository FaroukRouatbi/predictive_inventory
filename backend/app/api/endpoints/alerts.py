from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.reorder_alert import ReorderAlertResponse, ResolveAlertRequest
from app.crud import reorder_alert as crud_alert
from app.crud import product as crud_product

router = APIRouter()


@router.get("/", response_model=List[ReorderAlertResponse])
def read_unresolved_alerts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Returns all unresolved alerts across all products.
    This is the main dashboard view — what needs attention right now.
    """
    return crud_alert.get_unresolved_alerts(db=db, skip=skip, limit=limit)


@router.get("/all", response_model=List[ReorderAlertResponse])
def read_all_alerts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Returns all alerts including resolved ones.
    Useful for audit history.
    """
    return crud_alert.get_all_alerts(db=db, skip=skip, limit=limit)


@router.get("/product/{product_id}", response_model=List[ReorderAlertResponse])
def read_alerts_by_product(
    product_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    return crud_alert.get_alerts_by_product(
        db=db,
        product_id=product_id,
        skip=skip,
        limit=limit
    )


@router.get("/{alert_id}", response_model=ReorderAlertResponse)
def read_alert(alert_id: UUID, db: Session = Depends(get_db)):
    alert = crud_alert.get_alert(db=db, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found."
        )
    return alert


@router.put("/{alert_id}/resolve", response_model=ReorderAlertResponse)
def resolve_alert(
    alert_id: UUID,
    request: ResolveAlertRequest,
    db: Session = Depends(get_db)
):
    """
    Marks an alert as resolved. Call this when a reorder has been placed.
    Once resolved, a new alert can be triggered for the same product
    if stock drops below reorder_level again.
    """
    alert = crud_alert.resolve_alert(
        db=db,
        alert_id=alert_id,
        notes=request.notes
    )
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found."
        )
    return alert

@router.put("/{alert_id}/unresolve", response_model=ReorderAlertResponse)
def unresolve_alert(
    alert_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Reverts a resolved alert back to unresolved.
    Use when a reorder was marked complete by mistake.
    """
    alert = crud_alert.unresolve_alert(db=db, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found."
        )
    return alert