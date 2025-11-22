from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class WalletBase(BaseModel):
    user_id: UUID
    balance: int = Field(default=0, ge=0)


class WalletResponse(WalletBase):
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WalletTransactionBase(BaseModel):
    user_id: UUID
    amount: int
    transaction_type: str = Field(..., pattern="^(deposit|withdraw|refund|payment)$")
    booking_id: Optional[UUID] = None


class WalletTransactionCreate(WalletTransactionBase):
    pass


class WalletTransactionResponse(WalletTransactionBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class WalletDepositRequest(BaseModel):
    amount: int = Field(..., gt=0)

