import asyncpg
from typing import Optional
from uuid import UUID
from app.models.user import UserCreate, UserResponse, UserProfileCreate


class UserRepository:
    @staticmethod
    async def create(conn: asyncpg.Connection, user_data: UserCreate, password_hash: str) -> dict:
        """Create a new user"""
        query = """
            INSERT INTO users (mobile, password_hash)
            VALUES ($1, $2)
            RETURNING id, mobile, created_at
        """
        row = await conn.fetchrow(query, user_data.mobile, password_hash)
        return dict(row)
    
    @staticmethod
    async def get_by_mobile(conn: asyncpg.Connection, mobile: str) -> Optional[dict]:
        """Get user by mobile number"""
        query = "SELECT id, mobile, password_hash, created_at, updated_at FROM users WHERE mobile = $1"
        row = await conn.fetchrow(query, mobile)
        return dict(row) if row else None
    
    @staticmethod
    async def get_by_id(conn: asyncpg.Connection, user_id: UUID) -> Optional[dict]:
        """Get user by ID"""
        query = "SELECT id, mobile, created_at, updated_at FROM users WHERE id = $1"
        row = await conn.fetchrow(query, user_id)
        return dict(row) if row else None
    
    @staticmethod
    async def get_profile_id_by_name(conn: asyncpg.Connection, profile_name: str) -> Optional[UUID]:
        """Get profile ID by profile name"""
        query = "SELECT id FROM profiles WHERE name = $1"
        row = await conn.fetchrow(query, profile_name)
        return row['id'] if row else None
    
    @staticmethod
    async def create_profile(conn: asyncpg.Connection, profile_data: UserProfileCreate) -> dict:
        """Create a user profile (many-to-many relationship)"""
        # Get profile_id from profile_name
        profile_id = await UserRepository.get_profile_id_by_name(conn, profile_data.profile_type)
        if not profile_id:
            raise ValueError(f"Profile type '{profile_data.profile_type}' not found")
        
        query = """
            INSERT INTO user_profiles (user_id, profile_id)
            VALUES ($1, $2)
            ON CONFLICT (user_id, profile_id) DO NOTHING
            RETURNING id, user_id, profile_id, created_at
        """
        row = await conn.fetchrow(query, profile_data.user_id, profile_id)
        if row:
            # Get profile name for response
            profile_name = await conn.fetchval("SELECT name FROM profiles WHERE id = $1", profile_id)
            result = dict(row)
            result['profile_type'] = profile_name
            return result
        return None
    
    @staticmethod
    async def get_user_profiles(conn: asyncpg.Connection, user_id: UUID) -> list:
        """Get all profiles for a user (with profile names)"""
        query = """
            SELECT up.id, up.user_id, up.profile_id, p.name as profile_type, up.created_at
            FROM user_profiles up
            JOIN profiles p ON up.profile_id = p.id
            WHERE up.user_id = $1
        """
        rows = await conn.fetch(query, user_id)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def has_profile(conn: asyncpg.Connection, user_id: UUID, profile_type: str) -> bool:
        """Check if user has a specific profile"""
        query = """
            SELECT 1 FROM user_profiles up
            JOIN profiles p ON up.profile_id = p.id
            WHERE up.user_id = $1 AND p.name = $2
        """
        row = await conn.fetchrow(query, user_id, profile_type)
        return row is not None

