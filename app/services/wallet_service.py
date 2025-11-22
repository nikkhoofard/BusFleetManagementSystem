import asyncpg
from uuid import UUID
from app.repositories.wallet_repository import WalletRepository


class WalletService:
    @staticmethod
    async def get_balance(conn: asyncpg.Connection, user_id: UUID) -> dict:
        """Get wallet balance"""
        wallet = await WalletRepository.get_wallet(conn, user_id)
        if not wallet:
            wallet = await WalletRepository.create_wallet(conn, user_id)
        return {"balance": wallet['balance']}
    
    @staticmethod
    async def deposit(conn: asyncpg.Connection, user_id: UUID, amount: int) -> dict:
        """Deposit money to wallet"""
        async with conn.transaction():
            wallet = await WalletRepository.get_wallet(conn, user_id)
            if not wallet:
                wallet = await WalletRepository.create_wallet(conn, user_id)
            
            # Update balance
            updated = await WalletRepository.update_balance(conn, user_id, amount)
            
            # Create transaction record
            await WalletRepository.create_transaction(
                conn,
                user_id,
                amount,
                'deposit'
            )
            
            return {"balance": updated['balance']}
    
    @staticmethod
    async def get_transactions(conn: asyncpg.Connection, user_id: UUID, limit: int = 50) -> list:
        """Get transaction history"""
        return await WalletRepository.get_transactions(conn, user_id, limit)

