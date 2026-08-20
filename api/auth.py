import os
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


raw_pem = os.getenv("CLERK_PEM_PUBLIC_KEY", "")
CLERK_PEM_PUBLIC_KEY = raw_pem.replace("\\n", "\n")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            CLERK_PEM_PUBLIC_KEY,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token no contiene ID de usuario")
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token de Clerk inválido: {str(e)}"
        )