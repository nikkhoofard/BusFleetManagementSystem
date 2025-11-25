import asyncio
import asyncpg
from datetime import datetime, timedelta, timezone
from uuid import UUID
from app.core.config import settings
from app.core.security import get_password_hash
from app.repositories.user_repository import UserRepository
from app.repositories.wallet_repository import WalletRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.bus_repository import BusRepository
from app.repositories.trip_repository import TripRepository
from app.models.user import UserCreate, UserProfileCreate
from app.models.route import RouteCreate
from app.models.bus import BusCreate
from app.models.trip import TripCreate
from app.db.seeders import seed100kseats,seed_100k_reservation

async def seed_database():
    """Seed the database with initial data"""
    conn = await asyncpg.connect(settings.database_url)
    
    try:
        # Create admin user (with multiple profiles: admin, operator, passenger)
        print("Creating admin user...")
        admin_user = UserCreate(mobile="09120000000", password="admin123")
        admin_password_hash = get_password_hash(admin_user.password)
        admin = await UserRepository.create(conn, admin_user, admin_password_hash)
        
        # Create admin profiles - یک کاربر می‌تواند همزمان چندین نقش داشته باشد
        await UserRepository.create_profile(conn, UserProfileCreate(user_id=admin['id'], profile_type='admin'))
        await UserRepository.create_profile(conn, UserProfileCreate(user_id=admin['id'], profile_type='operator'))
        await UserRepository.create_profile(conn, UserProfileCreate(user_id=admin['id'], profile_type='passenger'))
        await WalletRepository.create_wallet(conn, admin['id'])
        await WalletRepository.update_balance(conn, admin['id'], 1000000)  # 1 million
        
        # Create sample users
        print("Creating sample users...")
        users = []
        for i in range(1, 5000):
            # شماره‌های فیک: 09 + 9 رقم = 11 کاراکتر
            # استفاده از 0912xxxxxxx (09 + 12 + 7 رقم)
            mobile = f"0912{i:07d}"  # 0912 + 0000001 = 09120000001 (11 کاراکتر)
            user_data = UserCreate(mobile=mobile, password="123456")
            password_hash = get_password_hash(user_data.password)
            user = await UserRepository.create(conn, user_data, password_hash)
            await UserRepository.create_profile(conn, UserProfileCreate(user_id=user['id'], profile_type='passenger'))
            await WalletRepository.create_wallet(conn, user['id'])
            await WalletRepository.update_balance(conn, user['id'], 500000)  # 500k
            users.append(user)
        
        # Create driver users (with multiple profiles: driver and passenger)
        print("Creating driver users...")
        drivers = []
        for i in range(1, 1000):
            # شماره‌های فیک: 09 + 9 رقم = 11 کاراکتر
            mobile = f"0913{i:07d}"  # 0913 + 0000001 = 09130000001 (11 کاراکتر)
            user_data = UserCreate(mobile=mobile, password="123456")
            password_hash = get_password_hash(user_data.password)
            user = await UserRepository.create(conn, user_data, password_hash)
            # یک کاربر می‌تواند همزمان راننده و مسافر باشد
            await UserRepository.create_profile(conn, UserProfileCreate(user_id=user['id'], profile_type='driver'))
            await UserRepository.create_profile(conn, UserProfileCreate(user_id=user['id'], profile_type='passenger'))
            await WalletRepository.create_wallet(conn, user['id'])
            drivers.append(user)
        
        # Create operator user
        print("Creating operator user...")
        operator_mobile = "09140000001"
        operator_data = UserCreate(mobile=operator_mobile, password="123456")
        operator_password_hash = get_password_hash(operator_data.password)
        operator = await UserRepository.create(conn, operator_data, operator_password_hash)
        await UserRepository.create_profile(conn, UserProfileCreate(user_id=operator['id'], profile_type='operator'))
        await WalletRepository.create_wallet(conn, operator['id'])
        
        # Create routes
        print("Creating routes...")
        routes_data = [
            RouteCreate(origin="قم", destination="اصفهان", distance_km=450),
            RouteCreate(origin="قم", destination="شیراز", distance_km=900),
            RouteCreate(origin="قم", destination="مشهد", distance_km=900),
            RouteCreate(origin="اصفهان", destination="شیراز", distance_km=500),
            RouteCreate(origin="قم", destination="تبریز", distance_km=600),
            RouteCreate(origin="قم", destination="کرمان", distance_km=700),
            RouteCreate(origin="قم", destination="کرمانشاه", distance_km=800),
            RouteCreate(origin="قم", destination="قم", distance_km=900),
            RouteCreate(origin="قم", destination="کردستان", distance_km=1000),
            RouteCreate(origin="تهران", destination="خراسان جنوبی", distance_km=1100),
            RouteCreate(origin="قم", destination="خراسان", distance_km=1200),
            RouteCreate(origin="قم", destination="خراسان رضوی", distance_km=1300),
            RouteCreate(origin="قم", destination="خراسان شمالی", distance_km=1400),
        ]
        routes = []
        for route_data in routes_data:
            route = await RouteRepository.create(conn, route_data)
            routes.append(route)
        
        # Create buses
        print("Creating buses...")
        buses = []
        for i, route in enumerate(routes[:]):  # Create 3 buses
            bus_data = BusCreate(
                plate_number=f"67ز{100+i}",
                capacity=40,
                route_id=route['id'],
                owner_id=operator['id'],
                driver_ids=[drivers[i % len(drivers)]['id']] if drivers else []
            )
            bus = await BusRepository.create(conn, bus_data)
            buses.append(bus)
        
        # Create trips and seats
        print("Creating trips and seats...")
        now = datetime.now(timezone.utc)
        for bus in buses:
            for day in range(30):  # 30 days of trips
                departure_time = now + timedelta(days=day, hours=8)
                arrival_time = departure_time + timedelta(hours=6)
                
                trip = await TripRepository.create(
                    conn,
                    bus['id'],
                    departure_time,
                    arrival_time,
                    "active"
                )
                
                # Create seats for this trip
                bus_info = await BusRepository.get_by_id(conn, bus['id'])
                capacity = bus_info['capacity'] if bus_info else 50
                
                for seat_num in range(1, capacity + 1):
                    # Price varies by seat number (window seats more expensive)
                    base_price = 500000  # 500k base
                    if seat_num <= 2 or seat_num >= capacity - 1:
                        price = base_price + 100000  # Window seats
                    else:
                        price = base_price
                    
                    await conn.execute("""
                        INSERT INTO seats (trip_id, seat_number, price)
                        VALUES ($1, $2, $3)
                    """, trip['id'], seat_num, price)
        
        print("Database seeded successfully!")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
    asyncio.run(seed100kseats.seed_seats())
    asyncio.run(seed_100k_reservation.seed_reservations())
    

