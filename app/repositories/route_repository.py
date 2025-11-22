import asyncpg
from typing import Optional
from uuid import UUID
from app.models.route import RouteCreate


class RouteRepository:
    @staticmethod
    async def create(conn: asyncpg.Connection, route_data: RouteCreate) -> dict:
        """Create a new route"""
        query = """
            INSERT INTO routes (origin, destination, distance_km)
            VALUES ($1, $2, $3)
            RETURNING id, origin, destination, distance_km, created_at
        """
        row = await conn.fetchrow(
            query,
            route_data.origin,
            route_data.destination,
            route_data.distance_km
        )
        return dict(row)
    
    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, route_id: UUID) -> Optional[dict]:
        """Get route by ID"""
        query = "SELECT id, origin, destination, distance_km, created_at FROM routes WHERE id = $1"
        row = await conn.fetchrow(query, route_id)
        return dict(row) if row else None

