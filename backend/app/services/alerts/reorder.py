from sqlalchemy.orm import Session
from uuid import UUID

from app.crud import reorder_alert as crud_alert
from app.crud import inventory as crud_inventory
from app.services.forecasting.engine import ForecastingEngine

engine = ForecastingEngine()


def check_and_create_alert(db: Session, product_id: UUID) -> None:
    """
    Called after every sale is recorded. Checks if stock has
    dropped to or below the reorder level and creates an alert
    if needed.

    This function is intentionally silent — it never raises
    exceptions. It runs as a background task after the sale
    response is already sent to the client, so errors here
    must not affect the sale transaction.
    """
    try:
        # Get current inventory state
        inventory = crud_inventory.get_inventory_by_product(db, product_id)
        if not inventory:
            return

        # Check if stock is at or below reorder threshold
        if inventory.quantity_on_hand > inventory.reorder_level:
            return  # Stock is fine, no alert needed

        # Check for existing unresolved alert — no duplicate spam
        if crud_alert.has_unresolved_alert(db, product_id):
            return  # Already alerted, waiting for resolution

        # Get forecast-based reorder recommendation
        recommended_quantity = _get_reorder_recommendation(db, product_id)

        # Create the alert
        crud_alert.create_alert(
            db=db,
            product_id=product_id,
            quantity_on_hand=inventory.quantity_on_hand,
            reorder_level=inventory.reorder_level,
            recommended_reorder_quantity=recommended_quantity,
            notes=f"Stock dropped to {inventory.quantity_on_hand} units "
                  f"(reorder level: {inventory.reorder_level}). "
                  f"Forecast-based reorder quantity: {recommended_quantity} units."
        )

    except Exception:
        # Silently swallow all errors — background tasks must never
        # crash or affect the main sale transaction
        pass


def _get_reorder_recommendation(db: Session, product_id: UUID) -> int:
    """
    Attempts to get a forecast-based reorder quantity.
    Falls back to a simple formula if forecasting fails
    (e.g. insufficient history for a new product).
    """
    try:
        report = engine.generate(
            db=db,
            product_id=product_id,
            horizon_days=30,
            history_days=90
        )
        return report.recommended_reorder_quantity

    except Exception:
        # Fallback: reorder enough for 30 days at reorder_level rate
        inventory = crud_inventory.get_inventory_by_product(db, product_id)
        if inventory:
            return inventory.reorder_level * 3
        return 30  # absolute fallback