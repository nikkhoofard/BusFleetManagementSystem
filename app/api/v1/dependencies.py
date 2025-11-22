from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID
import asyncpg
from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn: asyncpg.Connection = Depends(get_db)
) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = UUID(payload.get("sub"))
    user = await UserRepository.get_by_id(conn, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def require_profile(
    profile_type: str
):
    """Create a dependency that requires a specific profile"""
    async def _require_profile(
        current_user: dict = Depends(get_current_user),
        conn: asyncpg.Connection = Depends(get_db)
    ) -> dict:
        """Require user to have a specific profile"""
        profiles = await UserRepository.get_user_profiles(conn, current_user['id'])
        profile_types = [p['profile_type'] for p in profiles]
        
        if profile_type not in profile_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must have {profile_type} profile"
            )
        
        return current_user
    
    return _require_profile

