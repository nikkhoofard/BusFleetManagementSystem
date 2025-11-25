# scripts/seed_100k_reservations.py
import asyncio
import asyncpg
import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker

fake = Faker('fa_IR')

# تنظیمات
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fast_api"
TOTAL_RESERVATIONS = 100_000
BATCH_SIZE = 10_000

# متغیرهای سراسری
EXISTING_USER_IDS = []
SEAT_TRIP_MAP = {}  # seat_id → trip_id

async def fetch_existing_data(conn):
    global EXISTING_USER_IDS, SEAT_TRIP_MAP
    
    print("در حال دریافت کاربران و صندلی‌ها از دیتابیس...")

    # کاربران مسافر
    users = await conn.fetch("""
        SELECT u.id FROM users u
        JOIN user_profiles up ON u.id = up.user_id
        JOIN profiles p ON up.profile_id = p.id
        WHERE p.name = 'passenger'
        LIMIT 8000
    """)

    # صندلی‌ها + trip_id
    seats = await conn.fetch("""
        SELECT s.id, s.trip_id 
        FROM seats s
        JOIN trips t ON s.trip_id = t.id
        WHERE t.status = 'active'
    """)

    EXISTING_USER_IDS = [row['id'] for row in users]
    SEAT_TRIP_MAP = {row['id']: row['trip_id'] for row in seats}

    if not EXISTING_USER_IDS:
        print("هیچ مسافری پیدا نشد! اول چند تا کاربر با نقش passenger بساز")
        exit(1)
    if not SEAT_TRIP_MAP:
        print("هیچ صندلی‌ای پیدا نشد! اول سفر و صندلی بساز")
        exit(1)

    print(f"✓ {len(EXISTING_USER_IDS):,} مسافر و {len(SEAT_TRIP_MAP):,} صندلی آماده شد")
    return list(SEAT_TRIP_MAP.keys())  # بازگرداندن لیست seat_id ها

async def seed_reservations():
    conn = await asyncpg.connect(DATABASE_URL)
    available_seat_ids = await fetch_existing_data(conn)  # دریافت لیست صندلی‌ها

    # محدود کردن تعداد رزروها به تعداد صندلی‌های موجود
    total_to_create = min(TOTAL_RESERVATIONS, len(available_seat_ids))
    
    print(f"شروع ساخت {total_to_create:,} رزرو موقت...")
    print("پاکسازی جدول reservations برای شروع تازه...")

    await conn.execute("TRUNCATE TABLE reservations RESTART IDENTITY")

    # تکان دادن لیست برای رندم شدن
    random.shuffle(available_seat_ids)
    
    records = []
    now_utc = datetime.now(timezone.utc)
    base_start = now_utc - timedelta(days=60)

    for i in range(1, total_to_create + 1):
        user_id = random.choice(EXISTING_USER_IDS)
        seat_id = available_seat_ids.pop()  # برداشتن صندلی از لیست (هر صندلی فقط یک بار)
        trip_id = SEAT_TRIP_MAP[seat_id]

        created_at = base_start + timedelta(
            days=random.randint(0, 60),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        expires_at = created_at + timedelta(minutes=random.randint(5, 20))
        status = "held" if expires_at > now_utc else "expired"

        records.append((
            str(uuid.uuid4()),           # id
            str(user_id),                # user_id
            str(seat_id),                # seat_id
            str(trip_id),                # trip_id
            fake.first_name(),           # first_name
            fake.last_name(),            # last_name
            ''.join(random.choices('0123456789', k=10)),  # national_id
            random.choice([True, False]), # gender
            expires_at,                  # expires_at
            status,                      # status
            created_at                   # created_at
        ))

        if len(records) >= BATCH_SIZE:
            await conn.copy_records_to_table(
                'reservations',
                records=records,
                columns=(
                    'id', 'user_id', 'seat_id', 'trip_id',
                    'first_name', 'last_name', 'national_id', 'gender',
                    'expires_at', 'status', 'created_at'
                )
            )
            print(f"{BATCH_SIZE:,} رزرو اضافه شد (مجموع: {i:,})")
            records.clear()

    if records:
        await conn.copy_records_to_table(
            'reservations', records=records,
            columns=(
                'id', 'user_id', 'seat_id', 'trip_id',
                'first_name', 'last_name', 'national_id', 'gender',
                'expires_at', 'status', 'created_at'
            )
        )
        print(f"آخرین {len(records):,} رزرو اضافه شد")

    await conn.close()
    print(f"{total_to_create:,} رزرو موقت با موفقیت ساخته شد!")

if __name__ == "__main__":
    asyncio.run(seed_reservations())