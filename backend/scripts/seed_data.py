import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import random

from app.db.session import SessionLocal
from app.models.product import Product
from app.models.inventory import InventoryItem
from app.models.sales_record import SalesRecord
from app.models.enums import ProductCategory, Currency


# ── Seed Configuration ────────────────────────────────────────────────────────

DAYS_OF_HISTORY = 120  # 4 months of sales history

PRODUCTS = [
    {
        "sku": "ELEC-001",
        "name": "Wireless Headphones",
        "description": "Noise-cancelling over-ear headphones",
        "category": ProductCategory.ELECTRONICS,
        "price_cents": 9999,
        "currency": Currency.USD,
        # Sales pattern: stable ~5/day with slight upward trend
        "daily_avg": 5,
        "volatility": 1.0,
        "trend": 0.02,
        "seasonal": False,
    },
    {
        "sku": "CLTH-001",
        "name": "Winter Jacket",
        "description": "Insulated waterproof winter jacket",
        "category": ProductCategory.CLOTHING,
        "price_cents": 14999,
        "currency": Currency.USD,
        # Sales pattern: strong seasonal spike (cold months)
        "daily_avg": 3,
        "volatility": 2.0,
        "trend": 0.0,
        "seasonal": True,
    },
    {
        "sku": "FOOD-001",
        "name": "Protein Powder",
        "description": "Whey protein vanilla flavour 2kg",
        "category": ProductCategory.FOOD,
        "price_cents": 4999,
        "currency": Currency.USD,
        # Sales pattern: high volume, high volatility
        "daily_avg": 12,
        "volatility": 4.0,
        "trend": 0.05,
        "seasonal": False,
    },
    {
        "sku": "HOME-001",
        "name": "Air Purifier",
        "description": "HEPA filter air purifier for large rooms",
        "category": ProductCategory.HOME,
        "price_cents": 7499,
        "currency": Currency.USD,
        # Sales pattern: slow mover, low volatility
        "daily_avg": 2,
        "volatility": 0.5,
        "trend": 0.0,
        "seasonal": False,
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def generate_daily_quantity(day_index: int, config: dict) -> int:
    """
    Generates a realistic daily sales quantity based on:
    - Base average
    - Random volatility (noise)
    - Linear trend over time
    - Seasonal multiplier (weekly cycle simulation)
    """
    base = config["daily_avg"]
    noise = random.gauss(0, config["volatility"])
    trend = config["trend"] * day_index
    seasonal = (1.5 if day_index % 7 in [5, 6] else 1.0) if config["seasonal"] else 1.0

    quantity = int(max(0, (base + noise + trend) * seasonal))
    return quantity


# ── Main Seeder ───────────────────────────────────────────────────────────────

def seed():
    db = SessionLocal()

    try:
        # Clear existing data in correct FK order
        print("🧹 Clearing existing seed data...")
        db.query(SalesRecord).delete()
        db.query(InventoryItem).delete()
        db.query(Product).delete()
        db.commit()

        print("🌱 Seeding products and inventory...")

        for config in PRODUCTS:
            # Create product
            product = Product(
                id=uuid4(),
                sku=config["sku"],
                name=config["name"],
                description=config["description"],
                category=config["category"],
                price_cents=config["price_cents"],
                currency=config["currency"],
            )
            db.add(product)
            db.flush()  # get product.id without committing

            # Create inventory
            inventory = InventoryItem(
                id=uuid4(),
                product_id=product.id,
                quantity_on_hand=500,  # start with enough stock
                reorder_level=50,
            )
            db.add(inventory)
            db.flush()

            # Generate sales history
            print(f"  📦 Generating {DAYS_OF_HISTORY} days of sales for {config['name']}...")

            for day_index in range(DAYS_OF_HISTORY):
                sold_at = datetime.now(timezone.utc) - timedelta(days=DAYS_OF_HISTORY - day_index)
                quantity = generate_daily_quantity(day_index, config)

                if quantity <= 0:
                    continue

                sale = SalesRecord(
                    id=uuid4(),
                    product_id=product.id,
                    inventory_id=inventory.id,
                    quantity_sold=quantity,
                    price_at_sale=config["price_cents"],
                    sold_at=sold_at,
                )
                db.add(sale)

        db.commit()
        print("✅ Seed complete.")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()