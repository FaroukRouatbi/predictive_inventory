from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
from app.services.alerts.reorder import check_and_create_alert

from app.db.session import get_db
from app.schemas.sales_record import SalesRecordCreate, SalesRecordResponse
from app.crud import sales_record as crud_sales
from app.crud import product as crud_product
from app.crud import inventory as crud_inventory
from app.core.limiter import limiter

router = APIRouter()


@router.post(
    "/",
    response_model=SalesRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a sale",
    description="Records a sale and atomically deducts stock. Validates product exists, inventory matches, and sufficient stock is available. Triggers a reorder alert check in the background if stock drops below reorder level."
)
@limiter.limit("30/minute")
def record_sale(
    request: Request,
    sale_in: SalesRecordCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    product = crud_product.get_product(db, product_id=sale_in.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    inventory = crud_inventory.get_inventory_by_product(db, product_id=sale_in.product_id)
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found for this product.")

    if inventory.id != sale_in.inventory_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inventory_id does not match the inventory record for this product.")

    if inventory.quantity_on_hand < sale_in.quantity_sold:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient stock. Available: {inventory.quantity_on_hand}, Requested: {sale_in.quantity_sold}."
        )

    db_sale = crud_sales.create_sale(db=db, sale_in=sale_in)
    crud_inventory.adjust_stock(db=db, product_id=sale_in.product_id, delta=-sale_in.quantity_sold)
    background_tasks.add_task(check_and_create_alert, db, sale_in.product_id)
    return db_sale


@router.get(
    "/product/{product_id}",
    response_model=List[SalesRecordResponse],
    summary="Get sales history for a product",
    description="Returns paginated sales history for a specific product ordered by most recent first."
)
@limiter.limit("60/minute")
def read_sales_by_product(
    request: Request,
    product_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return crud_sales.get_sales_by_product(db=db, product_id=product_id, skip=skip, limit=limit)


@router.get(
    "/product/{product_id}/window",
    response_model=List[SalesRecordResponse],
    summary="Get sales within a date window",
    description="Returns all sales for a product between start_date and end_date. Dates must be ISO 8601 format."
)
@limiter.limit("60/minute")
def read_sales_in_window(
    request: Request,
    product_id: UUID,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    if start_date >= end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_date must be before end_date.")

    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    return crud_sales.get_sales_in_window(db=db, product_id=product_id, start_date=start_date, end_date=end_date)


@router.get(
    "/product/{product_id}/revenue",
    response_model=dict,
    summary="Get total revenue for a product",
    description="Returns total revenue in cents and dollars for a product. Optionally filter by date range. Uses price snapshots at time of sale for historical accuracy."
)
@limiter.limit("60/minute")
def read_product_revenue(
    request: Request,
    product_id: UUID,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    product = crud_product.get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    total_cents = crud_sales.get_total_revenue_by_product(db=db, product_id=product_id, start_date=start_date, end_date=end_date)
    return {
        "product_id": str(product_id),
        "total_revenue_cents": total_cents,
        "total_revenue_dollars": round(total_cents / 100, 2)
    }


@router.get(
    "/{sale_id}",
    response_model=SalesRecordResponse,
    summary="Get a sale by ID",
    description="Returns a single sale record by its UUID. Returns 404 if not found."
)
@limiter.limit("60/minute")
def read_sale(request: Request, sale_id: UUID, db: Session = Depends(get_db)):
    sale = crud_sales.get_sale(db=db, sale_id=sale_id)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found.")
    return sale


@router.delete(
    "/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sale record",
    description="Permanently deletes a sale record. Use only for correcting data entry errors. Returns 404 if not found."
)
@limiter.limit("30/minute")
def delete_sale(request: Request, sale_id: UUID, db: Session = Depends(get_db)):
    sale = crud_sales.delete_sale(db=db, sale_id=sale_id)
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found.")
    return None