import asyncpg
from uuid import UUID
from datetime import datetime, timezone
from app.repositories.bus_repository import BusRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.user_repository import UserRepository
from app.models.bus import BusCreate
from app.models.trip import TripCreate


class AdminService:
    @staticmethod
    async def create_bus(conn: asyncpg.Connection, bus_data: BusCreate) -> dict:
        """Create a new bus"""
        # Verify owner has operator profile
        has_operator = await UserRepository.has_profile(conn, bus_data.owner_id, 'operator')
        if not has_operator:
            raise ValueError("User must have operator profile to create a bus")
        
        # Verify drivers have driver profile
        for driver_id in bus_data.driver_ids:
            has_driver = await UserRepository.has_profile(conn, driver_id, 'driver')
            if not has_driver:
                raise ValueError(f"User {driver_id} must have driver profile")
        
        return await BusRepository.create(conn, bus_data)
    
    @staticmethod
    async def create_trip(conn: asyncpg.Connection, trip_data: TripCreate) -> dict:
        """Create a new trip"""
        return await TripRepository.create(
            conn,
            trip_data.bus_id,
            trip_data.departure_time,
            trip_data.arrival_time,
            trip_data.status
        )
    
    @staticmethod
    async def get_hourly_bookings(conn: asyncpg.Connection) -> list:
        """Get successful bookings per hour"""
        return await AdminRepository.get_hourly_bookings(conn)
    
    @staticmethod
    async def get_bus_revenue(
        conn: asyncpg.Connection,
        month: int = None,
        year: int = None
    ) -> list:
        """Get bus revenue per month"""
        if month is None:
            month = datetime.now(timezone.utc).month
        if year is None:
            year = datetime.now(timezone.utc).year
        
        return await AdminRepository.get_bus_revenue(conn, month, year)
    
    @staticmethod
    async def get_busiest_driver(conn: asyncpg.Connection) -> dict:
        """Get busiest driver"""
        return await AdminRepository.get_busiest_driver(conn)
    
    @staticmethod
    async def get_bus_drivers(conn: asyncpg.Connection) -> dict:
        """Get busiest driver"""
        return await AdminRepository.get_bus_drivers(conn)

    @staticmethod
    async def get_bus(conn: asyncpg.Connection) -> dict:
        """Get busiest driver"""
        return await BusRepository.get_bus(conn)

