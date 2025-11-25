from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional,List
import asyncpg
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user, require_profile
from app.services.admin_service import AdminService
from app.schemas.admin import (
    BusCreateRequest, TripCreateRequest, HourlyBookingsResponse,BusResponse,
    BusRevenueResponse, BusiestDriverResponse,BusDriversResponse,RouteCreate,RouteResponse
)
from app.models.bus import BusCreate
from app.models.trip import TripCreate
from app.repositories.route_repository import RouteRepository
router = APIRouter()


@router.post("/buses", response_model=dict)
async def create_bus(
    request: BusCreateRequest,
    current_user: dict = Depends(require_profile("operator")),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Create a new bus (operator/admin only)"""
    try:
        bus_data = BusCreate(**request.dict())
        result = await AdminService.create_bus(conn, bus_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trips", response_model=dict)
async def create_trip(
    request: TripCreateRequest,
    current_user: dict = Depends(require_profile("operator")),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Create a new trip (operator/admin only)"""
    try:
        trip_data = TripCreate(**request.dict())
        result = await AdminService.create_trip(conn, trip_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/hourly-bookings", response_model=list[HourlyBookingsResponse])
async def get_hourly_bookings(
    current_user: dict = Depends(require_profile("operator")),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get successful bookings per hour"""
    try:
        result = await AdminService.get_hourly_bookings(conn)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/bus-revenue", response_model=list[BusRevenueResponse])
async def get_bus_revenue(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020),
    current_user: dict = Depends(require_profile("operator")),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get reservations and revenue per bus per month"""
    try:
        result = await AdminService.get_bus_revenue(conn, month, year)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/busiest-driver", response_model=BusiestDriverResponse)
async def get_busiest_driver(
    current_user: dict = Depends(require_profile("operator")),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get driver with most trips"""
    try:
        result = await AdminService.get_busiest_driver(conn)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/bus-drivers", response_model=List[BusDriversResponse])
async def get_bus_drivers(
    current_user: dict = Depends(require_profile("operator")),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get driver with most trips"""
    try:
        result = await AdminService.get_bus_drivers(conn)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post(
    "/create-route",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ایجاد مسیر جدید",
    description="فقط ادمین می‌تواند مسیر جدید اضافه کند"
)
async def create_route(
    route_data: RouteCreate,
    conn: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(require_profile("operator")),  # بعداً اضافه کن
):
    try:
        route = await RouteRepository.create(conn, route_data)
        return route
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"خطا در ایجاد مسیر: {str(e)}"
        )
    
@router.get(
    "/get-all-route",
    response_model=List[RouteResponse],
    summary="لیست همه مسیرها"
)
async def get_all_routes(
    conn: asyncpg.Connection = Depends(get_db),
    current_user: dict = Depends(require_profile("operator")),
):
    routes = await RouteRepository.get_all(conn)
    return routes



@router.get("/get-all-bus",
            response_model=List[BusResponse],
            summary="لیست همه اتوبوس ها")
async def get_bus_drivers(
    current_user: dict = Depends(require_profile("operator")),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get driver with most trips"""
    try:
        result = await AdminService.get_bus(conn)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    