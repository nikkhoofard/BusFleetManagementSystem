import asyncpg
from typing import Optional
from datetime import datetime, timedelta, timezone
from uuid import UUID
import random


class SMSRepository:
    @staticmethod
    async def create_verification(conn: asyncpg.Connection, mobile: str) -> dict:
        """Create a new SMS verification code"""
        code = str(random.randint(100000, 999999))
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=5)
        
        query = """
            INSERT INTO sms_verifications (mobile, code, expires_at)
            VALUES ($1, $2, $3)
            RETURNING id, mobile, code, expires_at, verified, created_at
        """
        row = await conn.fetchrow(query, mobile, code, expires_at)
        return dict(row)
    
    @staticmethod
    async def verify_code(conn: asyncpg.Connection, mobile: str, code: str) -> Optional[dict]:
        """Verify SMS code"""
        query = """
            UPDATE sms_verifications
            SET verified = true
            WHERE mobile = $1 
              AND code = $2 
              AND verified = false
              AND expires_at > now()
            RETURNING id, mobile, code, expires_at, verified, created_at
        """
        row = await conn.fetchrow(query, mobile, code)
        return dict(row) if row else None
    
    @staticmethod
    async def get_latest_code(conn: asyncpg.Connection, mobile: str) -> Optional[dict]:
        """Get latest verification code for mobile"""
        query = """
            SELECT id, mobile, code, expires_at, verified, created_at
            FROM sms_verifications
            WHERE mobile = $1
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = await conn.fetchrow(query, mobile)
        return dict(row) if row else None

