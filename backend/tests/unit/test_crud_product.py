from app.crud.product import create_product, get_product, get_product_by_sku, update_product, delete_product
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.enums import ProductCategory, Currency


def make_product():
    """Helper that returns a valid ProductCreate schema."""
    return ProductCreate(
        sku="TEST-001",
        name="Test Product",
        description="A test product",
        category=ProductCategory.ELECTRONICS,
        price_cents=999,
        currency=Currency.USD
    )


def test_create_product(db):
    product_in = make_product()
    product = create_product(db=db, product=product_in)
    assert product is not None
    assert product.id is not None
    assert product.sku == "TEST-001"
    assert product.name == "Test Product"


def test_get_product(db):
    product_in = make_product()
    created = create_product(db=db, product=product_in)
    fetched = get_product(db=db, product_id=created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.sku == created.sku


def test_get_product_by_sku(db):
    product_in = make_product()
    created = create_product(db=db, product=product_in)
    fetched = get_product_by_sku(db=db, sku="TEST-001")
    assert fetched is not None
    assert fetched.id == created.id


def test_update_product(db):
    product_in = make_product()
    created = create_product(db=db, product=product_in)
    updated = update_product(
        db=db,
        product_id=created.id,
        product_update=ProductUpdate(name="Updated Name")
    )
    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.sku == "TEST-001"  # unchanged field


def test_delete_product(db):
    product_in = make_product()
    created = create_product(db=db, product=product_in)
    deleted = delete_product(db=db, product_id=created.id)
    assert deleted is not None
    fetched = get_product(db=db, product_id=created.id)
    assert fetched is None


def test_create_duplicate_sku_returns_none(db):
    product_in = make_product()
    create_product(db=db, product=product_in)
    duplicate = create_product(db=db, product=product_in)
    assert duplicate is None