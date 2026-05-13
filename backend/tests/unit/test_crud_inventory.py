from app.crud.product import create_product
from app.crud.inventory import (
    create_inventory,
    get_inventory_by_product,
    update_inventory,
    delete_inventory,
    get_low_stock_items
)
from app.schemas.product import ProductCreate
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.models.enums import ProductCategory, Currency


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_product(db):
    """
    Every inventory test needs a product first.
    Inventory has a FK to Product — can't exist without one.
    """
    product_in = ProductCreate(
        sku="TEST-001",
        name="Test Product",
        description="A test product",
        category=ProductCategory.ELECTRONICS,
        price_cents=999,
        currency=Currency.USD
    )
    return create_product(db=db, product_in=product_in)


def make_inventory(db, quantity=100, reorder_level=10):
    """
    Creates a product + inventory record.
    quantity and reorder_level are parameterized so tests
    can control stock levels without repeating code.
    """
    product = make_product(db)
    inventory_in = InventoryCreate(
        product_id=product.id,
        quantity_on_hand=quantity,
        reorder_level=reorder_level
    )
    return create_inventory(db=db, inventory_in=inventory_in)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_create_inventory(db):
    """
    Verifies that creating an inventory record works correctly
    and all fields are stored as expected.
    """
    inventory = make_inventory(db)
    assert inventory is not None
    assert inventory.id is not None
    assert inventory.quantity_on_hand == 100
    assert inventory.reorder_level == 10
    assert inventory.product_id is not None


def test_get_inventory_by_product(db):
    """
    Verifies that we can retrieve an inventory record
    using its associated product_id.
    """
    created = make_inventory(db)

    fetched = get_inventory_by_product(db=db, product_id=created.product_id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.product_id == created.product_id
    assert fetched.quantity_on_hand == created.quantity_on_hand


def test_get_inventory_by_product_not_found(db):
    """
    Verifies that querying a non-existent product_id returns None.
    Tests the None contract — CRUD never raises, just returns None.
    """
    from uuid import uuid4
    result = get_inventory_by_product(db=db, product_id=uuid4())
    assert result is None


def test_update_inventory(db):
    """
    Verifies that updating inventory fields works correctly.
    Uses exclude_unset pattern — only updated fields change,
    others stay the same.
    """
    created = make_inventory(db)

    updated = update_inventory(
        db=db,
        product_id=created.product_id,
        inventory_update=InventoryUpdate(quantity_on_hand=50)
    )

    assert updated is not None
    assert updated.quantity_on_hand == 50
    assert updated.reorder_level == 10  # unchanged — exclude_unset working


def test_update_inventory_not_found(db):
    """
    Verifies that updating a non-existent record returns None.
    """
    from uuid import uuid4
    result = update_inventory(
        db=db,
        product_id=uuid4(),
        inventory_update=InventoryUpdate(quantity_on_hand=50)
    )
    assert result is None


def test_delete_inventory(db):
    """
    Verifies that deleting an inventory record works and
    the record is no longer retrievable after deletion.
    """
    created = make_inventory(db)

    deleted = delete_inventory(db=db, product_id=created.product_id)
    assert deleted is not None

    # Verify it's actually gone
    fetched = get_inventory_by_product(db=db, product_id=created.product_id)
    assert fetched is None


def test_delete_inventory_not_found(db):
    """
    Verifies that deleting a non-existent record returns None.
    """
    from uuid import uuid4
    result = delete_inventory(db=db, product_id=uuid4())
    assert result is None


def test_get_low_stock_items(db):
    """
    Verifies that low stock detection works correctly.
    Creates two items — one below reorder level, one above —
    and checks only the low stock item is returned.
    """
    # Low stock item — quantity(5) <= reorder_level(10)
    low_stock = make_inventory(db, quantity=5, reorder_level=10)

    # Healthy stock item — needs different SKU so no duplicate conflict
    product_in = ProductCreate(
        sku="TEST-002",
        name="Healthy Product",
        description="Well stocked",
        category=ProductCategory.ELECTRONICS,
        price_cents=999,
        currency=Currency.USD
    )
    from app.crud.product import create_product
    healthy_product = create_product(db=db, product_in=product_in)
    inventory_in = InventoryCreate(
        product_id=healthy_product.id,
        quantity_on_hand=100,
        reorder_level=10
    )
    create_inventory(db=db, inventory_in=inventory_in)

    low_stock_items = get_low_stock_items(db=db)

    assert len(low_stock_items) == 1
    assert low_stock_items[0].id == low_stock.id