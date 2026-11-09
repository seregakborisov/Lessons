from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidTokenError

SECRET_KEY = "cb32e9ded39339be7b9d739e58464af275470a13907d45673cf780caee2d68d0"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme)]):
    
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(payload["sub"])
        role = payload["role"]

    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise credentials_exception

    if role not in ("Admin", "Teacher", "Student"):
        raise credentials_exception

    return {
        "id": user_id,
        "role": role,
    }