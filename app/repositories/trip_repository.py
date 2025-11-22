import asyncpg
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class TripRepository:
    @staticmethod
    async def create(conn: asyncpg.Connection, bus_id: UUID, departure_time: datetime, 
                     arrival_time: datetime, status: str = "active") -> dict:
        """Create a new trip"""
        query = """
            INSERT INTO trips (bus_id, departure_time, arrival_time, status)
            VALUES ($1, $2, $3, $4)
            RETURNING id, bus_id, departure_time, arrival_time, status, created_at
        """
        row = await conn.fetchrow(query, bus_id, departure_time, arrival_time, status)
        return dict(row)
    
    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, trip_id: UUID) -> Optional[dict]:
        """Get trip by ID"""
        query = """
            SELECT t.id, t.bus_id, t.departure_time, t.arrival_time, t.status, t.created_at,
                   b.plate_number, b.capacity, r.origin, r.destination
            FROM trips t
            JOIN buses b ON t.bus_id = b.id
            JOIN routes r ON b.route_id = r.id
            WHERE t.id = $1
        """
        row = await conn.fetchrow(query, trip_id)
        return dict(row) if row else None
    
    @staticmethod
    async def get_available_trips(
        conn: asyncpg.Connection,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[dict]:
        """Get available trips with available seats"""
        base_query = """
            SELECT DISTINCT
                t.id as trip_id,
                t.bus_id,
                b.plate_number,
                t.departure_time,
                t.arrival_time,
                r.origin,
                r.destination,
                s.id as seat_id,
                s.seat_number,
                s.price
            FROM trips t
            JOIN buses b ON t.bus_id = b.id
            JOIN routes r ON b.route_id = r.id
            JOIN seats s ON s.trip_id = t.id
            LEFT JOIN reservations res ON res.seat_id = s.id 
                AND res.status = 'held' 
                AND res.expires_at > now()
            WHERE t.status = 'active'
              AND res.id IS NULL
              AND s.id NOT IN (
                  SELECT seat_id FROM bookings WHERE status = 'confirmed'
              )
        """
        
        conditions = []
        params = []
        param_count = 0
        
        if origin:
            param_count += 1
            conditions.append(f"r.origin ILIKE ${param_count}")
            params.append(f"%{origin}%")
        
        if destination:
            param_count += 1
            conditions.append(f"r.destination ILIKE ${param_count}")
            params.append(f"%{destination}%")
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        if sort_by == "price_asc":
            base_query += " ORDER BY s.price ASC, t.departure_time ASC"
        elif sort_by == "price_desc":
            base_query += " ORDER BY s.price DESC, t.departure_time ASC"
        else:
            base_query += " ORDER BY t.departure_time ASC, s.price ASC"
        
        rows = await conn.fetch(base_query, *params)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def get_seat(conn: asyncpg.Connection, seat_id: UUID) -> Optional[dict]:
        """Get seat by ID"""
        query = """
            SELECT s.id, s.trip_id, s.seat_number, s.price,
                   t.departure_time, t.arrival_time
            FROM seats s
            JOIN trips t ON s.trip_id = t.id
            WHERE s.id = $1
        """
        row = await conn.fetchrow(query, seat_id)
        return dict(row) if row else None

