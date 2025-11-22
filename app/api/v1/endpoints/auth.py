from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import SendVerificationRequest, VerifyCodeRequest, LoginRequest, TokenResponse

router = APIRouter()


@router.post("/send-verification", response_model=dict)
async def send_verification(
    request: SendVerificationRequest,
    conn: asyncpg.Connection = Depends(get_db)
):
    """Send SMS verification code"""
    try:
        result = await AuthService.send_verification(conn, request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-code", response_model=TokenResponse)
async def verify_code(
    request: VerifyCodeRequest,
    conn: asyncpg.Connection = Depends(get_db)
):
    """Verify SMS code and register/login"""
    try:
        result = await AuthService.verify_code(conn, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    conn: asyncpg.Connection = Depends(get_db)
):
    """Login with mobile and password"""
    try:
        result = await AuthService.login(conn, request.mobile, request.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

