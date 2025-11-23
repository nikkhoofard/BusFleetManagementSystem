from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
import asyncpg
from uuid import UUID
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.services.booking_service import BookingService
from app.schemas.booking import (
    ReserveSeatRequest, ReserveSeatResponse, PayBookingRequest,
    BookingResponse, ReservationResponse, AvailableTripResponse, AvailableTripsQuery
)

router = APIRouter()


@router.post("/reserve-seat", response_model=ReserveSeatResponse)
async def reserve_seat(
    request: ReserveSeatRequest,
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Reserve a seat for 10 minutes"""
    try:
        result = await BookingService.reserve_seat(conn, current_user['id'], request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reservation_id}/pay", response_model=BookingResponse)
async def pay_booking(
    reservation_id: str,
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Pay for reserved booking"""

    try:
        reservation_uuid = UUID(reservation_id)
        result = await BookingService.pay_booking(conn, current_user['id'], reservation_uuid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reservations/{reservation_id}", response_model=ReservationResponse)
async def cancel_reservation(
    reservation_id: str,
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Cancel a reservation"""
    from uuid import UUID
    try:
        reservation_uuid = UUID(reservation_id)
        result = await BookingService.cancel_reservation(conn, current_user['id'], reservation_uuid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Cancel a confirmed booking"""
    from uuid import UUID
    try:
        booking_uuid = UUID(booking_id)
        result = await BookingService.cancel_booking(conn, current_user['id'], booking_uuid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available", response_model=list[AvailableTripResponse])
async def get_available_trips(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, pattern="^(price_asc|price_desc)$"),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get available trips with seats"""
    try:
        result = await BookingService.get_available_trips(conn, origin, destination, sort_by)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-bookings", response_model=list[BookingResponse])
async def get_my_bookings(
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get user's bookings"""
    try:
        result = await BookingService.get_user_bookings(conn, current_user['id'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-reservations", response_model=list[ReservationResponse])
async def get_my_reservations(
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get user's active reservations"""
    try:
        result = await BookingService.get_user_reservations(conn, current_user['id'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

