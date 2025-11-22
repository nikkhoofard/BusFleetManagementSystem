from fastapi import APIRouter
from app.api.v1.endpoints import auth, bookings, wallet, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

