from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.services.wallet_service import WalletService
from app.schemas.wallet import WalletBalanceResponse, DepositRequest, TransactionResponse

router = APIRouter()


@router.get("/balance", response_model=WalletBalanceResponse)
async def get_balance(
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get wallet balance"""
    try:
        result = await WalletService.get_balance(conn, current_user['id'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deposit", response_model=WalletBalanceResponse)
async def deposit(
    request: DepositRequest,
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Deposit money to wallet"""
    try:
        result = await WalletService.deposit(conn, current_user['id'], request.amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    current_user: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_db)
):
    """Get transaction history"""
    try:
        result = await WalletService.get_transactions(conn, current_user['id'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

