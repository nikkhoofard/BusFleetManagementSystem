import asyncpg
from typing import List, Optional
from uuid import UUID
from app.models.bus import BusCreate


class BusRepository:
    @staticmethod
    async def create(conn: asyncpg.Connection, bus_data: BusCreate) -> dict:
        """Create a new bus"""
        query = """
            INSERT INTO buses (plate_number, capacity, route_id, owner_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id, plate_number, capacity, route_id, owner_id, created_at
        """
        row = await conn.fetchrow(
            query,
            bus_data.plate_number,
            bus_data.capacity,
            bus_data.route_id,
            bus_data.owner_id
        )
        bus = dict(row)
        
        # Add drivers if provided
        if bus_data.driver_ids:
            for driver_id in bus_data.driver_ids:
                await BusRepository.add_driver(conn, bus['id'], driver_id)
        
        return bus
    
    @staticmethod
    async def add_driver(conn: asyncpg.Connection, bus_id: UUID, driver_id: UUID) -> dict:
        """Add driver to bus"""
        query = """
            INSERT INTO bus_drivers (bus_id, driver_id, is_active)
            VALUES ($1, $2, true)
            ON CONFLICT (bus_id, driver_id) DO UPDATE SET is_active = true
            RETURNING id, bus_id, driver_id, is_active, created_at
        """
        row = await conn.fetchrow(query, bus_id, driver_id)
        return dict(row)
    
    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, bus_id: UUID) -> Optional[dict]:
        """Get bus by ID"""
        query = """
            SELECT b.id, b.plate_number, b.capacity, b.route_id, b.owner_id, b.created_at,
                   r.origin, r.destination
            FROM buses b
            JOIN routes r ON b.route_id = r.id
            WHERE b.id = $1
        """
        row = await conn.fetchrow(query, bus_id)
        return dict(row) if row else None
    
    @staticmethod
    async def get_bus_drivers(conn: asyncpg.Connection, bus_id: UUID) -> List[dict]:
        """Get all drivers for a bus"""
        query = """
            SELECT bd.id, bd.bus_id, bd.driver_id, bd.is_active, bd.created_at,
                   u.mobile as driver_mobile
            FROM bus_drivers bd
            JOIN users u ON bd.driver_id = u.id
            WHERE bd.bus_id = $1 AND bd.is_active = true
        """
        rows = await conn.fetch(query, bus_id)
        return [dict(row) for row in rows]

