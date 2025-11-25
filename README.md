# Bus Fleet Management System

A comprehensive FastAPI-based system for managing intercity bus fleet, ticket booking, and reporting.

## Features

- **User Management**: Multiple profiles per user (passenger, operator, driver, admin)
- **SMS Verification**: Registration via ippanel SMS service
- **Wallet System**: Deposit, payment, and refund functionality
- **Professional Booking System**: 
  - 10-minute seat reservation
  - Prevents double booking with database-level constraints
  - Automatic expiration of old reservations
- **Admin Features**: Create buses, trips, and view reports
- **Concurrency Handling**: Row-level locking prevents race conditions

## Tech Stack

- FastAPI (latest)
- asyncpg (PostgreSQL async driver)
- Pydantic (validation)
- JWT (authentication)
- ippanel (SMS service)

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database URL, JWT secret, and ippanel API key
```

3. **Run migrations:**
```bash
python app/db/migrate.py
```

4. **Seed database:**
```bash
python app/db/seeders/seeder.py
```

5. **Run the application:**
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/send-verification` - Send SMS verification code
- `POST /api/v1/auth/verify-code` - Verify code and register/login
- `POST /api/v1/auth/login` - Login with mobile/password

### Wallet
- `GET /api/v1/wallet/balance` - Get wallet balance
- `POST /api/v1/wallet/deposit` - Deposit money
- `GET /api/v1/wallet/transactions` - Get transaction history

### Bookings
- `POST /api/v1/bookings/reserve-seat` - Reserve a seat (10 minutes)
- `POST /api/v1/bookings/{reservation_id}/pay` - Pay for reservation
- `DELETE /api/v1/bookings/reservations/{reservation_id}` - Cancel reservation
- `DELETE /api/v1/bookings/{booking_id}/cancel` - Cancel booking (with refund)
- `GET /api/v1/bookings/available` - List available trips
- `GET /api/v1/bookings/my-bookings` - Get user's bookings
- `GET /api/v1/bookings/my-reservations` - Get active reservations

### Admin
- `POST /api/v1/admin/buses` - Create bus (operator only)
- `POST /api/v1/admin/trips` - Create trip (operator only)
- `POST /api/v1/admin/create-route` - Create route (operator only)
- `GET /api/v1/admin/reports/hourly-bookings` - Bookings per hour
- `GET /api/v1/admin/reports/bus-revenue` - Revenue per bus per month
- `GET /api/v1/admin/reports/busiest-driver` - Driver with most trips
- `GET /api/v1/admin/get-all-route` - get all route(operator only)
- `GET /api/v1/admin/get-all-bus` - Get all active bus(operator only)

## Database Schema

The system uses the following key tables:
- `users` - User accounts
- `user_profiles` - User roles (passenger/operator/driver)
- `routes` - Bus routes
- `buses` - Bus information with owner
- `bus_drivers` - Many-to-many relationship (bus can have multiple drivers)
- `trips` - Scheduled trips
- `seats` - Seats for each trip with individual pricing
- `reservations` - Temporary seat holds (10 minutes)
- `bookings` - Confirmed ticket purchases
- `user_wallets` - User wallet balances
- `wallet_transactions` - Transaction history

## Default Credentials

After seeding:
- Admin: `09120000000` / `admin123`
- Sample users: `09120000001-5` / `123456`
- Drivers: `09130000001-3` / `123456`
- Operator: `09140000001` / `123456`

## Notes

- All bookings must be paid within 10 minutes of reservation
- Maximum 20 confirmed bookings per user per day
- Background task automatically expires old reservations every minute
- All operations use database transactions for atomicity

