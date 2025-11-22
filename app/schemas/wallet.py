from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class WalletBalanceResponse(BaseModel):
    balance: int


class DepositRequest(BaseModel):
    amount: int = Field(..., gt=0)


class TransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: int
    transaction_type: str
    booking_id: Optional[UUID] = None
    created_at: datetime

