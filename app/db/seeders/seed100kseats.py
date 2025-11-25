# scripts/seed_100k_seats.py
import asyncio
import asyncpg
import uuid
import random
from datetime import datetime, timedelta, timezone

# تنظیمات — فقط اینو عوض کن
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fast_api"
TOTAL_SEATS = 100_000
SEATS_PER_TRIP = 40  # مثلاً هر اتوبوس 40 صندلی داره
BATCH_SIZE = 10_000

async def ensure_enough_trips(conn):
    """اگه سفر کم باشه، خودکار می‌سازه تا صندلی جا داشته باشه"""
    trip_count = await conn.fetchval("SELECT COUNT(*) FROM trips WHERE status = 'active'")
    needed_trips = (TOTAL_SEATS // SEATS_PER_TRIP) + 10  # کمی بیشتر

    if trip_count >= needed_trips:
        print(f"سفر کافی هست: {trip_count:,}")
        return

    print(f"سفر کمه! {needed_trips - trip_count:,} سفر جدید می‌سازم...")

    # یه اتوبوس و مسیر نمونه بساز (یا از موجود استفاده کن)
    bus_id = await conn.fetchval("SELECT id FROM buses LIMIT 1")
    if not bus_id:
        print("هیچ اتوبوسی پیدا نشد! اول یه اتوبوس بساز")
        exit(1)

    # تاریخ شروع: از امروز تا ۶ ماه بعد
    base_date = datetime.now(timezone.utc)
    records = []

    for i in range(needed_trips - trip_count):
        departure = base_date + timedelta(days=random.randint(0, 180), hours=random.randint(0, 23))
        arrival = departure + timedelta(hours=random.randint(8, 20))

        records.append((
            str(uuid.uuid4()),
            str(bus_id),
            departure,
            arrival,
            'active',
            datetime.now(timezone.utc)
        ))

        if len(records) >= 1000:
            await conn.copy_records_to_table(
                'trips',
                records=records,
                columns=('id', 'bus_id', 'departure_time', 'arrival_time', 'status', 'created_at')
            )
            records.clear()

    if records:
        await conn.copy_records_to_table(
            'trips', records=records,
            columns=('id', 'bus_id', 'departure_time', 'arrival_time', 'status', 'created_at')
        )
    print(f"{needed_trips - trip_count:,} سفر جدید ساخته شد")

async def seed_seats():
    conn = await asyncpg.connect(DATABASE_URL)

    print("در حال بررسی تعداد سفرها...")
    await ensure_enough_trips(conn)

    # پاک کردن صندلی‌های قبلی (اختیاری)
    print("پاکسازی صندلی‌های قبلی...")
    await conn.execute("TRUNCATE TABLE reservations, seats RESTART IDENTITY CASCADE")

    # همه trip_idهای فعال رو بگیر
    trip_ids = [row['id'] for row in await conn.fetch("SELECT id FROM trips WHERE status = 'active'")]
    print(f"{len(trip_ids):,} سفر فعال برای صندلی‌سازی پیدا شد")

    records = []
    seat_counter = 0

    print(f"شروع ساخت {TOTAL_SEATS:,} صندلی...")

    for trip_id in trip_ids:
        for seat_num in range(1, SEATS_PER_TRIP + 1):
            if seat_counter >= TOTAL_SEATS:
                break

            price = random.randint(150_000, 800_000)  # قیمت واقعی

            records.append((
                str(uuid.uuid4()),   # id
                str(trip_id),        # trip_id
                seat_num,            # seat_number
                price                # price
            ))

            seat_counter += 1

            if len(records) >= BATCH_SIZE:
                await conn.copy_records_to_table(
                    'seats',
                    records=records,
                    columns=('id', 'trip_id', 'seat_number', 'price')
                )
                print(f"{BATCH_SIZE:,} صندلی اضافه شد (مجموع: {seat_counter:,})")
                records.clear()

        if seat_counter >= TOTAL_SEATS:
            break

    # آخرین بچ
    if records:
        await conn.copy_records_to_table(
            'seats', records=records,
            columns=('id', 'trip_id', 'seat_number', 'price')
        )
        print(f"آخرین {len(records):,} صندلی اضافه شد")

    await conn.close()
    print(f"100,000 صندلی با موفقیت ساخته شد!")

if __name__ == "__main__":
    asyncio.run(seed_seats())