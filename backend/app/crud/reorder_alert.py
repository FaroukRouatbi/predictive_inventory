from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from app.models.reorder_alert import ReorderAlert


def create_alert(
    db: Session,
    product_id: UUID,
    quantity_on_hand: int,
    reorder_level: int,
    recommended_reorder_quantity: int,
    notes: Optional[str] = None
) -> ReorderAlert:
    alert = ReorderAlert(
        product_id=product_id,
        quantity_on_hand=quantity_on_hand,
        reorder_level=reorder_level,
        recommended_reorder_quantity=recommended_reorder_quantity,
        notes=notes
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_alert(db: Session, alert_id: UUID) -> Optional[ReorderAlert]:
    return db.query(ReorderAlert).filter(ReorderAlert.id == alert_id).first()


def get_alerts_by_product(
    db: Session,
    product_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> list[ReorderAlert]:
    return (
        db.query(ReorderAlert)
        .filter(ReorderAlert.product_id == product_id)
        .order_by(ReorderAlert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_unresolved_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[ReorderAlert]:
    return (
        db.query(ReorderAlert)
        .filter(ReorderAlert.is_resolved == False)
        .order_by(ReorderAlert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def has_unresolved_alert(db: Session, product_id: UUID) -> bool:
    """
    Checks if an unresolved alert already exists for this product.
    Used to prevent duplicate alert spam — one active alert per
    product at a time is sufficient.
    """
    return (
        db.query(ReorderAlert)
        .filter(
            and_(
                ReorderAlert.product_id == product_id,
                ReorderAlert.is_resolved == False
            )
        )
        .first()
    ) is not None


def resolve_alert(
    db: Session,
    alert_id: UUID,
    notes: Optional[str] = None
) -> Optional[ReorderAlert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None

    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    if notes:
        alert.notes = notes

    db.commit()
    db.refresh(alert)
    return alert


def get_all_alerts(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> list[ReorderAlert]:
    return (
        db.query(ReorderAlert)
        .order_by(ReorderAlert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def unresolve_alert(
    db: Session,
    alert_id: UUID,
) -> Optional[ReorderAlert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None

    alert.is_resolved = False
    alert.resolved_at = None
    alert.notes = None

    db.commit()
    db.refresh(alert)
    return alert