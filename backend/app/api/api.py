from fastapi import APIRouter
from app.api.endpoints import products, inventory, sales_record, forecast, alerts, auth

api_router = APIRouter()
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(sales_record.router, prefix="/sales", tags=["Sales"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
