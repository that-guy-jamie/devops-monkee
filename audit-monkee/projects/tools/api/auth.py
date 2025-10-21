from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from .settings import settings

security = HTTPBearer(auto_error=False)

def require_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # If JWT_SECRET not set, open endpoints
    if not settings.jwt_secret:
        return None

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing Authorization')

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=['HS256'])
        return payload
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
