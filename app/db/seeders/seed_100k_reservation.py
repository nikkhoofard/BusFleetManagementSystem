# scripts/seed_100k_trips.py
import asyncio
import asyncpg
import uuid
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker('fa_IR')

# تنظیمات
TOTAL_TRIPS = 100_000
BATCH_SIZE = 10_000  # هر بار ۱۰٬۰۰۰ تا
DATABASE_URL = "postgresql://postgres:password@localhost/busfleet"  # عوض کن

# لیست از bus_id و route_id واقعی که قبلاً ساختی (یا می‌تونی از دیتابیس بکشی)
# اینجا یه نمونه می‌ذارم — بعداً خودکار می‌گیریم
SAMPLE_BUS_IDS = []  # بعداً پر میشه
SAMPLE_ROUTE_IDS = []  # بعداً پر میشه

async def get_existing_ids(conn):
    global SAMPLE_BUS_IDS, SAMPLE_ROUTE_IDS
    buses = await conn.fetch("SELECT id FROM buses")
    routes = await conn.fetch("SELECT id FROM routes")
    SAMPLE_BUS_IDS = [row['id'] for row in buses]
    SAMPLE_ROUTE_IDS = [row['id'] for row in routes]
    
    if len(SAMPLE_BUS_IDS) == 0:
        print("هیچ اتوبوسی پیدا نشد! اول چند تا اتوبوس بساز")
        exit(1)
    if len(SAMPLE_ROUTE_IDS) == 0:
        print("هیچ مسیری پیدا نشد! اول چند تا route بساز")
        exit(1)

async def seed_trips():
    conn = await asyncpg.connect(DATABASE_URL)
    
    print("در حال دریافت اتوبوس‌ها و مسیرها...")
    await get_existing_ids(conn)
    
    print(f"شروع ساخت {TOTAL_TRIPS:,} سفر...")

    # پاک کردن سفرهای قبلی (اختیاری)
    await conn.execute("TRUNCATE TABLE trips RESTART IDENTITY")

    # آماده‌سازی داده‌ها برای COPY
    records = []
    base_date = datetime(2025, 1, 1)

    for i in range(TOTAL_TRIPS):
        bus_id = random.choice(SAMPLE_BUS_IDS)
        route_id = random.choice(SAMPLE_ROUTE_IDS)
        
        # تاریخ تصادفی در سال ۱۴۰۴
        departure = base_date + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(0, 23),
            minutes=random.choice([0, 30])
        )
        arrival = departure + timedelta(hours=random.randint(6, 20))  # سفر ۶ تا ۲۰ ساعته
        
        records.append((
            str(uuid.uuid4()),      # id
            str(bus_id),            # bus_id
            str(route_id),          # route_id
            departure,              # departure_time
            arrival,                # arrival_time
            random.choice(['active', 'completed', 'cancelled']),  # status
            datetime.utcnow()       # created_at
        ))

        # هر ۱۰٬۰۰۰ تا یه بار بنویس
        if len(records) >= BATCH_SIZE:
            await conn.copy_records_to_table(
                'trips',
                records=records,
                columns=('id', 'bus_id', 'route_id', 'departure_time', 'arrival_time', 'status', 'created_at')
            )
            print(f"✓ {len(records):,} سفر اضافه شد (مجموع: {i+1:,})")
            records = []

    # بقیه رو بنویس
    if records:
        await conn.copy_records_to_table(
            'trips',
            records=records,
            columns=('id', 'bus_id', 'route_id', 'departure_time', 'arrival_time', 'status', 'created_at')
        )
        print(f"آخرین {len(records):,} سفر اضافه شد")

    await conn.close()
    print(f"100,000 سفر با موفقیت ساخته شد!")

if __name__ == "__main__":
    asyncio.run(seed_trips())