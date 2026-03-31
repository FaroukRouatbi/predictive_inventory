from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from app.models.sales_record import SalesRecord
from app.schemas.sales_record import SalesRecordCreate


def create_sale(db: Session, sale_in: SalesRecordCreate) -> SalesRecord:
    data = sale_in.model_dump()

    # If sold_at not provided, let the DB handle it via server_default
    if data.get("sold_at") is None:
        data.pop("sold_at")

    db_sale = SalesRecord(**data)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def get_sale(db: Session, sale_id: UUID) -> Optional[SalesRecord]:
    return db.query(SalesRecord).filter(SalesRecord.id == sale_id).first()


def get_sales_by_product(
    db: Session,
    product_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> list[SalesRecord]:
    return (
        db.query(SalesRecord)
        .filter(SalesRecord.product_id == product_id)
        .order_by(SalesRecord.sold_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_sales_in_window(
    db: Session,
    product_id: UUID,
    start_date: datetime,
    end_date: datetime
) -> list[SalesRecord]:
    """
    Fetch all sales for a product within a time window.
    This is the core query the forecasting engine will use.
    """
    return (
        db.query(SalesRecord)
        .filter(SalesRecord.product_id == product_id)
        .filter(SalesRecord.sold_at >= start_date)
        .filter(SalesRecord.sold_at <= end_date)
        .order_by(SalesRecord.sold_at.asc())
        .all()
    )


def get_daily_sales_aggregates(
    db: Session,
    product_id: UUID,
    start_date: datetime,
    end_date: datetime
) -> list[dict]:
    """
    Returns daily total quantity sold for a product within a window.
    Used by the forecasting engine to build the time series.

    Returns: [{"date": date, "total_quantity": int}, ...]
    """
    results = (
        db.query(
            func.date_trunc('day', SalesRecord.sold_at).label("date"),
            func.sum(SalesRecord.quantity_sold).label("total_quantity")
        )
        .filter(SalesRecord.product_id == product_id)
        .filter(SalesRecord.sold_at >= start_date)
        .filter(SalesRecord.sold_at <= end_date)
        .group_by(func.date_trunc('day', SalesRecord.sold_at))
        .order_by(func.date_trunc('day', SalesRecord.sold_at).asc())
        .all()
    )

    return [{"date": row.date, "total_quantity": int(row.total_quantity)} for row in results]


def get_total_revenue_by_product(
    db: Session,
    product_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> int:
    """
    Returns total revenue in cents for a product.
    Optionally filtered by date window.
    """
    query = db.query(
        func.sum(SalesRecord.quantity_sold * SalesRecord.price_at_sale)
    ).filter(SalesRecord.product_id == product_id)

    if start_date:
        query = query.filter(SalesRecord.sold_at >= start_date)
    if end_date:
        query = query.filter(SalesRecord.sold_at <= end_date)

    result = query.scalar()
    return result or 0


def delete_sale(db: Session, sale_id: UUID) -> Optional[SalesRecord]:
    """
    Hard delete — only for correcting data entry errors.
    Returns None if not found.
    """
    db_sale = get_sale(db, sale_id)
    if not db_sale:
        return None
    db.delete(db_sale)
    db.commit()
    return db_sale