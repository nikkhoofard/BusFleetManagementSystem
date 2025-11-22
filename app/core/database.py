import asyncpg
from typing import Optional
from app.core.config import settings


class Database:
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def create_pool(cls):
        """Create database connection pool"""
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
        return cls._pool
    
    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """Get database connection pool"""
        if cls._pool is None:
            await cls.create_pool()
        return cls._pool
    
    @classmethod
    async def close_pool(cls):
        """Close database connection pool"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
    
    @classmethod
    async def execute(cls, query: str, *args):
        """Execute a query"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    @classmethod
    async def fetch(cls, query: str, *args):
        """Fetch multiple rows"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    @classmethod
    async def fetchrow(cls, query: str, *args):
        """Fetch a single row"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    @classmethod
    async def fetchval(cls, query: str, *args):
        """Fetch a single value"""
        pool = await cls.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Dependency for FastAPI
async def get_db():
    """Database dependency for FastAPI"""
    pool = await Database.get_pool()
    async with pool.acquire() as conn:
        yield conn

