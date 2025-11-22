import asyncpg
from datetime import datetime, timedelta
from uuid import UUID
from app.repositories.user_repository import UserRepository
from app.repositories.sms_repository import SMSRepository
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.sms import sms_service
from app.models.user import UserCreate, UserProfileCreate
from app.schemas.auth import SendVerificationRequest, VerifyCodeRequest


class AuthService:
    @staticmethod
    async def send_verification(conn: asyncpg.Connection, request: SendVerificationRequest) -> dict:
        """Send SMS verification code"""
        verification = await SMSRepository.create_verification(conn, request.mobile)
        
        # Send SMS via ippanel
        await sms_service.send_verification_code(request.mobile, verification['code'])
        
        return {
            "message": "Verification code sent",
            "mobile": request.mobile
        }
    
    @staticmethod
    async def verify_code(conn: asyncpg.Connection, request: VerifyCodeRequest) -> dict:
        """Verify SMS code and register/login user"""
        verification = await SMSRepository.verify_code(conn, request.mobile, request.code)
        
        if not verification:
            raise ValueError("Invalid or expired verification code")
        
        # Check if user exists
        user = await UserRepository.get_by_mobile(conn, request.mobile)
        
        if not user:
            # Register new user
            if not request.password:
                raise ValueError("Password is required for registration")
            
            password_hash = get_password_hash(request.password)
            user_data = UserCreate(mobile=request.mobile, password=request.password)
            user = await UserRepository.create(conn, user_data, password_hash)
            
            # Create default passenger profile
            profile_data = UserProfileCreate(user_id=user['id'], profile_type='passenger')
            await UserRepository.create_profile(conn, profile_data)
            
            # Create wallet
            from app.repositories.wallet_repository import WalletRepository
            await WalletRepository.create_wallet(conn, user['id'])
        else:
            # Existing user - verify password if provided
            if request.password:
                if not verify_password(request.password, user['password_hash']):
                    raise ValueError("Invalid password")
        
        # Create JWT token
        token = create_access_token(data={"sub": str(user['id']), "mobile": user['mobile']})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user['id']
        }
    
    @staticmethod
    async def login(conn: asyncpg.Connection, mobile: str, password: str) -> dict:
        """Login with mobile and password"""
        user = await UserRepository.get_by_mobile(conn, mobile)
        
        if not user:
            raise ValueError("Invalid mobile or password")
        
        if not verify_password(password, user['password_hash']):
            raise ValueError("Invalid mobile or password")
        
        # Create JWT token
        token = create_access_token(data={"sub": str(user['id']), "mobile": user['mobile']})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user['id']
        }
    
    @staticmethod
    async def get_current_user(conn: asyncpg.Connection, user_id: UUID) -> dict:
        """Get current user info"""
        user = await UserRepository.get_by_id(conn, user_id)
        if not user:
            raise ValueError("User not found")
        
        profiles = await UserRepository.get_user_profiles(conn, user_id)
        user['profiles'] = [p['profile_type'] for p in profiles]
        
        return user

