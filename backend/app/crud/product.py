from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_product_by_sku(db: Session, sku: str):
    return db.query(Product).filter(Product.sku == sku).first()


def get_product(db: Session, product_id: UUID):
    return db.query(Product).filter(Product.id == product_id).first()
    # Returns None on miss — endpoint raises the 404


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.model_dump())
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
    except IntegrityError:
        db.rollback()
        return None  # Endpoint raises 409
    return db_product


def update_product(db: Session, product_id: UUID, product_update: ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None  # Endpoint raises 404

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    try:
        db.commit()
        db.refresh(db_product)
    except IntegrityError:
        db.rollback()
        return None  # Endpoint raises 409
    return db_product


def delete_product(db: Session, product_id: UUID):
    db_product = get_product(db, product_id)
    if not db_product:
        return None  # Endpoint raises 404

    db.delete(db_product)
    db.commit()
    return db_product