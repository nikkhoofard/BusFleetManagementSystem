import asyncpg
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta,timezone   


class BookingRepository:
    @staticmethod
    async def create_reservation(
        conn: asyncpg.Connection,
        user_id: UUID,
        seat_id: UUID,
        trip_id: UUID,
        first_name: str,
        last_name: str,
        national_id: str,
        gender: bool,
        expires_at: datetime
    ) -> dict:
        """Create a reservation (with SELECT FOR UPDATE to prevent double booking)"""
        # First, lock the seat to prevent concurrent reservations
        query_lock = """
            SELECT id, trip_id, seat_number, price
            FROM seats
            WHERE id = $1
            FOR UPDATE
        """
        seat = await conn.fetchrow(query_lock, seat_id)
        if not seat:
            raise ValueError("Seat not found")
        
        # Check if seat is already reserved
        query_check = """
            SELECT id FROM reservations
            WHERE seat_id = $1 
              AND status = 'held'
              AND expires_at > now()
        """
        existing = await conn.fetchrow(query_check, seat_id)
        if existing:
            raise ValueError("Seat is already reserved")
        
        # Create reservation
        query = """
            INSERT INTO reservations (user_id, seat_id, trip_id, first_name, last_name, national_id, gender, expires_at, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'held')
            RETURNING id, user_id, seat_id, trip_id, first_name, last_name, national_id, gender, expires_at, status, created_at
        """
        row = await conn.fetchrow(query, user_id, seat_id, trip_id, first_name, last_name, national_id, gender, expires_at)
        return dict(row)
    
    @staticmethod
    async def get_reservation(conn: asyncpg.Connection, reservation_id: UUID) -> Optional[dict]:
        """Get reservation by ID"""
        query = """
            SELECT id, user_id, seat_id, trip_id, first_name, last_name, national_id, gender, expires_at, status, created_at
            FROM reservations
            WHERE id = $1
        """
        row = await conn.fetchrow(query, reservation_id)
        return dict(row) if row else None
    
    @staticmethod
    async def cancel_reservation(conn: asyncpg.Connection, reservation_id: UUID) -> dict:
        """Cancel a reservation"""
        query = """
            UPDATE reservations
            SET status = 'cancelled'
            WHERE id = $1 AND status = 'held'
            RETURNING id, user_id, seat_id, trip_id, first_name, last_name, national_id, gender, expires_at, status, created_at
        """
        row = await conn.fetchrow(query, reservation_id)
        if not row:
            raise ValueError("Reservation not found or already processed")
        return dict(row)
    
    @staticmethod
    async def create_booking(
        conn: asyncpg.Connection,
        reservation_id: UUID,
        price_paid: int
    ) -> dict:
        """Create booking from reservation"""
        # Get reservation details
        reservation = await BookingRepository.get_reservation(conn, reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        
        if reservation['status'] != 'held':
            raise ValueError("Reservation is not in held status")
        
        if reservation['expires_at'] < datetime.now(timezone.utc):
            raise ValueError("Reservation has expired")
        
        # Create booking
        query = """
            INSERT INTO bookings (
                user_id, trip_id, seat_id, first_name, last_name, 
                national_id, gender, price_paid, status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'confirmed')
            RETURNING id, user_id, trip_id, seat_id, first_name, last_name,
                      national_id, gender, price_paid, status, created_at, cancelled_at
        """
        row = await conn.fetchrow(
            query,
            reservation['user_id'],
            reservation['trip_id'],
            reservation['seat_id'],
            reservation['first_name'],
            reservation['last_name'],
            reservation['national_id'],
            reservation['gender'],
            price_paid
        )
        
        # Update reservation status
        await conn.execute(
            "UPDATE reservations SET status = 'confirmed' WHERE id = $1",
            reservation_id
        )
        
        return dict(row)
    
    @staticmethod
    async def get_user_bookings(conn: asyncpg.Connection, user_id: UUID, limit: int = 50) -> List[dict]:
        """Get user's bookings"""
        query = """
            SELECT id, user_id, trip_id, seat_id, first_name, last_name,
                   national_id, gender, price_paid, status, created_at, cancelled_at
            FROM bookings
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        rows = await conn.fetch(query, user_id, limit)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def get_user_reservations(conn: asyncpg.Connection, user_id: UUID) -> List[dict]:
        """Get user's active reservations"""
        query = """
            SELECT id, user_id, seat_id, trip_id, first_name, last_name, national_id, gender, expires_at, status, created_at
            FROM reservations
            WHERE user_id = $1 AND status = 'held' AND expires_at > now()
            ORDER BY created_at DESC
        """
        rows = await conn.fetch(query, user_id)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def cancel_booking(conn: asyncpg.Connection, booking_id: UUID) -> dict:
        """Cancel a booking"""
        query = """
            UPDATE bookings
            SET status = 'cancelled', cancelled_at = now()
            WHERE id = $1 AND status = 'confirmed'
            RETURNING id, user_id, trip_id, seat_id, first_name, last_name,
                      national_id, gender, price_paid, status, created_at, cancelled_at
        """
        row = await conn.fetchrow(query, booking_id)
        if not row:
            raise ValueError("Booking not found or already cancelled")
        return dict(row)
    
    @staticmethod
    async def get_daily_booking_count(conn: asyncpg.Connection, user_id: UUID, date: datetime) -> int:
        """Get count of confirmed bookings for user on a specific date"""
        query = """
            SELECT COUNT(*) as count
            FROM bookings
            WHERE user_id = $1
              AND status = 'confirmed'
              AND DATE(created_at) = DATE($2)
        """
        count = await conn.fetchval(query, user_id, date)
        return count or 0
    
    @staticmethod
    async def expire_reservations(conn: asyncpg.Connection) -> int:
        """Expire old reservations"""
        query = """
            UPDATE reservations
            SET status = 'expired'
            WHERE status = 'held' AND expires_at < now()
        """
        result = await conn.execute(query)
        return int(result.split()[-1]) if result else 0

    @staticmethod
    async def cleanup_expired_reservations(conn: asyncpg.Connection):
        await conn.execute("""
            DELETE FROM reservations 
            WHERE expires_at < NOW() AT TIME ZONE 'utc'
        """)

    # یا فقط برای یه صندلی خاص (سریع‌تر و بهتر)
    @staticmethod
    async def delete_expired_reservation_for_seat(conn: asyncpg.Connection, seat_id: UUID):
        await conn.execute("""
            DELETE FROM reservations 
            WHERE seat_id = $1 
              AND expires_at < NOW() AT TIME ZONE 'utc'
        """, seat_id)

# چک کردن رزرو فعال
    @staticmethod
    async def get_active_reservation_for_seat(conn: asyncpg.Connection, seat_id: UUID):
        return await conn.fetchrow("""
            SELECT * FROM reservations 
            WHERE seat_id = $1 
              AND expires_at > NOW() AT TIME ZONE 'utc'
        """, seat_id)   