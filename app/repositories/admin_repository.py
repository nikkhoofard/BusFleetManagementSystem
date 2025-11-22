import asyncpg
from typing import List
from datetime import datetime


class AdminRepository:
    @staticmethod
    async def get_hourly_bookings(conn: asyncpg.Connection) -> List[dict]:
        """Get successful bookings per hour"""
        query = """
            SELECT 
                EXTRACT(HOUR FROM created_at)::int as hour,
                COUNT(*)::int as bookings_count
            FROM bookings
            WHERE status = 'confirmed'
            GROUP BY EXTRACT(HOUR FROM created_at)
            ORDER BY hour
        """
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def get_bus_revenue(conn: asyncpg.Connection, month: int, year: int) -> List[dict]:
        """Get reservations and revenue per bus per month"""
        query = """
            SELECT 
                b.id as bus_id,
                b.plate_number,
                EXTRACT(MONTH FROM bk.created_at)::int as month,
                EXTRACT(YEAR FROM bk.created_at)::int as year,
                COUNT(bk.id)::int as bookings_count,
                COALESCE(SUM(bk.price_paid), 0)::bigint as total_revenue
            FROM buses b
            JOIN trips t ON t.bus_id = b.id
            JOIN bookings bk ON bk.trip_id = t.id
            WHERE bk.status = 'confirmed'
              AND EXTRACT(MONTH FROM bk.created_at) = $1
              AND EXTRACT(YEAR FROM bk.created_at) = $2
            GROUP BY b.id, b.plate_number, EXTRACT(MONTH FROM bk.created_at), EXTRACT(YEAR FROM bk.created_at)
            ORDER BY total_revenue DESC
        """
        rows = await conn.fetch(query, month, year)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def get_busiest_driver(conn: asyncpg.Connection) -> dict:
        """Get driver with most trips"""
        query = """
            SELECT 
                bd.driver_id,
                u.mobile as driver_mobile,
                COUNT(DISTINCT t.id)::int as trips_count
            FROM bus_drivers bd
            JOIN users u ON bd.driver_id = u.id
            JOIN buses b ON bd.bus_id = b.id
            JOIN trips t ON t.bus_id = b.id
            WHERE bd.is_active = true
            GROUP BY bd.driver_id, u.mobile
            ORDER BY trips_count DESC
            LIMIT 1
        """
        row = await conn.fetchrow(query)
        return dict(row) if row else {"driver_id": None, "driver_mobile": None, "trips_count": 0}

