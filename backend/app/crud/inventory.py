from sqlalchemy.orm import Session
from sqlalchemy import update as sql_update
from uuid import UUID

from app.models.inventory import InventoryItem
from app.schemas.inventory import InventoryCreate, InventoryUpdate


def get_inventory_by_product(db: Session, product_id: UUID):
    return (
        db.query(InventoryItem)
        .filter(InventoryItem.product_id == product_id)
        .first()
    )  # Returns None if not found — endpoint handles the 404


def get_all_inventory(db: Session, skip: int = 0, limit: int = 100):
    return db.query(InventoryItem).offset(skip).limit(limit).all()


def create_inventory(db: Session, inventory_in: InventoryCreate):
    # Duplicate check removed — endpoint handles this via IntegrityError catch
    db_inventory = InventoryItem(**inventory_in.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_inventory(db: Session, product_id: UUID, inventory_update: InventoryUpdate):
    db_inventory = get_inventory_by_product(db, product_id)
    if not db_inventory:
        return None  # Endpoint raises 404

    update_data = inventory_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def delete_inventory(db: Session, product_id: UUID):
    db_inventory = get_inventory_by_product(db, product_id)
    if not db_inventory:
        return None  # Endpoint raises 404

    db.delete(db_inventory)
    db.commit()
    return db_inventory


def update_stock_level(db: Session, product_id: UUID, new_quantity: int):
    """
    Atomic overwrite. Used for manual corrections (e.g. physical stock count).
    Race condition risk in high-traffic — use adjust_stock for increments.
    """
    db_inventory = get_inventory_by_product(db, product_id)
    if not db_inventory:
        return None

    # Atomic update — bypasses ORM object state to prevent race conditions
    db.execute(
        sql_update(InventoryItem)
        .where(InventoryItem.product_id == product_id)
        .values(quantity_on_hand=new_quantity)
    )
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def adjust_stock(db: Session, product_id: UUID, delta: int):
    """
    Atomic increment/decrement. Use this for sales and restocks — never
    read-modify-write manually, as concurrent requests can cause data loss.
    """
    # Atomic SQL-level adjustment — no race condition possible
    db.execute(
        sql_update(InventoryItem)
        .where(InventoryItem.product_id == product_id)
        .where(InventoryItem.quantity_on_hand + delta >= 0)  # Guard at DB level
        .values(quantity_on_hand=InventoryItem.quantity_on_hand + delta)
    )
    db.commit()

    db_inventory = get_inventory_by_product(db, product_id)
    if not db_inventory:
        return None
    return db_inventory


def get_low_stock_items(db: Session):
    return (
        db.query(InventoryItem)
        .filter(InventoryItem.quantity_on_hand <= InventoryItem.reorder_level)
        .all()
    )


