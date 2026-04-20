from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud import product as crud_product
from app.main import limiter


router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_new_product(request: Request, product_in: ProductCreate, db: Session = Depends(get_db)):
    product = crud_product.create_product(db=db, product=product_in)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A product with this SKU already exists."
        )
    return product


@router.get("/", response_model=List[ProductResponse])
@limiter.limit("60/minute")
def read_products(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_product.get_products(db=db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
@limiter.limit("60/minute")
def read_product(request: Request, product_id: UUID, db: Session = Depends(get_db)):
    product = crud_product.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
@limiter.limit("30/minute")
def update_existing_product(
    request: Request,
    product_id: UUID,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = crud_product.update_product(
        db=db, product_id=product_id, product_update=product_in
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def delete_existing_product(request: Request, product_id: UUID, db: Session = Depends(get_db)):
    product = crud_product.delete_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    return None
