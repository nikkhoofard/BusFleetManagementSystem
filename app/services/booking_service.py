import asyncpg
from datetime import datetime, timedelta
from uuid import UUID
from app.repositories.booking_repository import BookingRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.wallet_repository import WalletRepository
from app.schemas.booking import ReserveSeatRequest


class BookingService:
    MAX_DAILY_BOOKINGS = 20
    RESERVATION_DURATION_MINUTES = 10
    
    @staticmethod
    async def reserve_seat(
        conn: asyncpg.Connection,
        user_id: UUID,
        request: ReserveSeatRequest
    ) -> dict:
        """Reserve a seat for 10 minutes"""
        async with conn.transaction():
            # Check daily booking limit
            today = datetime.utcnow()
            daily_count = await BookingRepository.get_daily_booking_count(conn, user_id, today)
            if daily_count >= BookingService.MAX_DAILY_BOOKINGS:
                raise ValueError(f"Daily booking limit reached (max {BookingService.MAX_DAILY_BOOKINGS})")
            
            # Verify seat exists and get price
            seat = await TripRepository.get_seat(conn, request.seat_id)
            if not seat:
                raise ValueError("Seat not found")
            
            if seat['trip_id'] != request.trip_id:
                raise ValueError("Seat does not belong to this trip")
            
            # Create reservation (with locking)
            expires_at = datetime.utcnow() + timedelta(minutes=BookingService.RESERVATION_DURATION_MINUTES)
            reservation = await BookingRepository.create_reservation(
                conn,
                user_id,
                request.seat_id,
                request.trip_id,
                request.first_name,
                request.last_name,
                request.national_id,
                request.gender,
                expires_at
            )
            
            return {
                "reservation_id": reservation['id'],
                "expires_at": reservation['expires_at'],
                "payment_deadline": reservation['expires_at']
            }
    
    @staticmethod
    async def pay_booking(
        conn: asyncpg.Connection,
        user_id: UUID,
        reservation_id: UUID
    ) -> dict:
        """Pay for reserved booking"""
        async with conn.transaction():
            # Get reservation
            reservation = await BookingRepository.get_reservation(conn, reservation_id)
            if not reservation:
                raise ValueError("Reservation not found")
            
            if reservation['user_id'] != user_id:
                raise ValueError("Reservation does not belong to this user")
            
            if reservation['status'] != 'held':
                raise ValueError("Reservation is not in held status")
            
            if reservation['expires_at'] < datetime.utcnow():
                raise ValueError("Reservation has expired")
            
            # Get seat and passenger info from reservation
            seat = await TripRepository.get_seat(conn, reservation['seat_id'])
            if not seat:
                raise ValueError("Seat not found")
            
            # Get wallet
            wallet = await WalletRepository.get_wallet(conn, user_id)
            if not wallet:
                wallet = await WalletRepository.create_wallet(conn, user_id)
            
            # Check balance
            if wallet['balance'] < seat['price']:
                raise ValueError("Insufficient wallet balance")
            
            # Get reservation details - we need passenger info
            # For now, we'll need to store it in reservation or get it from request
            # Let's assume we need to pass it separately or store it in reservation
            # Actually, we need to modify the reservation to store passenger info
            # For now, let's create a simplified version
            
            # Deduct from wallet
            await WalletRepository.update_balance(conn, user_id, -seat['price'])
            
            # Create transaction record
            await WalletRepository.create_transaction(
                conn,
                user_id,
                -seat['price'],
                'payment'
            )
            
            # Create booking from reservation (passenger info is already in reservation)
            booking = await BookingRepository.create_booking(
                conn,
                reservation_id,
                seat['price']
            )
            
            return booking
    
    @staticmethod
    async def cancel_reservation(
        conn: asyncpg.Connection,
        user_id: UUID,
        reservation_id: UUID
    ) -> dict:
        """Cancel a reservation"""
        reservation = await BookingRepository.get_reservation(conn, reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        
        if reservation['user_id'] != user_id:
            raise ValueError("Reservation does not belong to this user")
        
        if reservation['status'] != 'held':
            raise ValueError("Reservation cannot be cancelled")
        
        return await BookingRepository.cancel_reservation(conn, reservation_id)
    
    @staticmethod
    async def cancel_booking(
        conn: asyncpg.Connection,
        user_id: UUID,
        booking_id: UUID
    ) -> dict:
        """Cancel a confirmed booking and refund"""
        async with conn.transaction():
            booking = await BookingRepository.get_user_bookings(conn, user_id)
            booking_dict = next((b for b in booking if b['id'] == booking_id), None)
            
            if not booking_dict:
                raise ValueError("Booking not found")
            
            if booking_dict['status'] != 'confirmed':
                raise ValueError("Booking cannot be cancelled")
            
            # Cancel booking
            cancelled = await BookingRepository.cancel_booking(conn, booking_id)
            
            # Refund to wallet
            await WalletRepository.update_balance(conn, user_id, cancelled['price_paid'])
            await WalletRepository.create_transaction(
                conn,
                user_id,
                cancelled['price_paid'],
                'refund',
                booking_id
            )
            
            return cancelled
    
    @staticmethod
    async def get_available_trips(
        conn: asyncpg.Connection,
        origin: str = None,
        destination: str = None,
        sort_by: str = None
    ) -> list:
        """Get available trips with seats"""
        trips = await TripRepository.get_available_trips(conn, origin, destination, sort_by)
        
        # Group by trip
        trips_dict = {}
        for trip in trips:
            trip_id = trip['trip_id']
            if trip_id not in trips_dict:
                trips_dict[trip_id] = {
                    "trip_id": trip_id,
                    "bus_id": trip['bus_id'],
                    "plate_number": trip['plate_number'],
                    "departure_time": trip['departure_time'],
                    "arrival_time": trip['arrival_time'],
                    "origin": trip['origin'],
                    "destination": trip['destination'],
                    "available_seats": []
                }
            trips_dict[trip_id]["available_seats"].append({
                "seat_id": trip['seat_id'],
                "seat_number": trip['seat_number'],
                "price": trip['price']
            })
        
        return list(trips_dict.values())
    
    @staticmethod
    async def get_user_bookings(conn: asyncpg.Connection, user_id: UUID) -> list:
        """Get user's bookings"""
        return await BookingRepository.get_user_bookings(conn, user_id)
    
    @staticmethod
    async def get_user_reservations(conn: asyncpg.Connection, user_id: UUID) -> list:
        """Get user's active reservations"""
        return await BookingRepository.get_user_reservations(conn, user_id)

