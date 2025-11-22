import asyncpg
from typing import Optional
from uuid import UUID
from datetime import datetime


class WalletRepository:
    @staticmethod
    async def get_wallet(conn: asyncpg.Connection, user_id: UUID) -> Optional[dict]:
        """Get user wallet"""
        query = "SELECT user_id, balance, updated_at FROM user_wallets WHERE user_id = $1"
        row = await conn.fetchrow(query, user_id)
        return dict(row) if row else None
    
    @staticmethod
    async def create_wallet(conn: asyncpg.Connection, user_id: UUID) -> dict:
        """Create wallet for user"""
        query = """
            INSERT INTO user_wallets (user_id, balance)
            VALUES ($1, 0)
            ON CONFLICT (user_id) DO NOTHING
            RETURNING user_id, balance, updated_at
        """
        row = await conn.fetchrow(query, user_id)
        if not row:
            # Wallet already exists, fetch it
            return await WalletRepository.get_wallet(conn, user_id)
        return dict(row)
    
    @staticmethod
    async def update_balance(conn: asyncpg.Connection, user_id: UUID, amount: int) -> dict:
        """Update wallet balance (atomic operation)"""
        query = """
            UPDATE user_wallets
            SET balance = balance + $2, updated_at = now()
            WHERE user_id = $1
            RETURNING user_id, balance, updated_at
        """
        row = await conn.fetchrow(query, user_id, amount)
        return dict(row)
    
    @staticmethod
    async def create_transaction(
        conn: asyncpg.Connection,
        user_id: UUID,
        amount: int,
        transaction_type: str,
        booking_id: Optional[UUID] = None
    ) -> dict:
        """Create wallet transaction"""
        query = """
            INSERT INTO wallet_transactions (user_id, amount, transaction_type, booking_id)
            VALUES ($1, $2, $3, $4)
            RETURNING id, user_id, amount, transaction_type, booking_id, created_at
        """
        row = await conn.fetchrow(query, user_id, amount, transaction_type, booking_id)
        return dict(row)
    
    @staticmethod
    async def get_transactions(conn: asyncpg.Connection, user_id: UUID, limit: int = 50) -> list:
        """Get user transaction history"""
        query = """
            SELECT id, user_id, amount, transaction_type, booking_id, created_at
            FROM wallet_transactions
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        rows = await conn.fetch(query, user_id, limit)
        return [dict(row) for row in rows]

