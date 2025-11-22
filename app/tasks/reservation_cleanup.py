import asyncio
from app.core.database import Database
from app.repositories.booking_repository import BookingRepository


async def cleanup_expired_reservations():
    """Periodically clean up expired reservations"""
    while True:
        try:
            pool = await Database.get_pool()
            async with pool.acquire() as conn:
                count = await BookingRepository.expire_reservations(conn)
                if count > 0:
                    print(f"Expired {count} reservations")
        except Exception as e:
            print(f"Error cleaning up reservations: {e}")
        
        # Run every minute
        await asyncio.sleep(60)


def start_reservation_cleanup_task():
    """Start the background task for cleaning up expired reservations"""
    asyncio.create_task(cleanup_expired_reservations())

