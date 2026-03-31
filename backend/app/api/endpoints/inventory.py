from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse
from app.crud import inventory as crud_inventory
from app.crud import product as crud_product

router = APIRouter()


@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def initialize_inventory(inventory_in: InventoryCreate, db: Session = Depends(get_db)):
    # Issue 1 fix: actually check the return value
    product = crud_product.get_product(db, product_id=inventory_in.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    # Issue 2 fix: catch duplicate inventory records cleanly
    try:
        return crud_inventory.create_inventory(db=db, inventory_in=inventory_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An inventory record for this product already exists."
        )


@router.get("/", response_model=List[InventoryResponse])
def read_all_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_inventory.get_all_inventory(db=db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=InventoryResponse)
def read_inventory(product_id: UUID, db: Session = Depends(get_db)):
    inventory = crud_inventory.get_inventory_by_product(db, product_id)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found."
        )
    return inventory


@router.put("/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: UUID,
    inventory_in: InventoryUpdate,
    db: Session = Depends(get_db),
):
    updated = crud_inventory.update_inventory(
        db=db,
        product_id=product_id,
        inventory_update=inventory_in,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found."
        )
    return updated


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(product_id: UUID, db: Session = Depends(get_db)):
    deleted = crud_inventory.delete_inventory(db, product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found."
        )
    return None