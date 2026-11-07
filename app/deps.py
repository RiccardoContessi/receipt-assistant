from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import CurrentUser

FAKE_TOKENS: dict[str, CurrentUser] = {
    "token-muller": CurrentUser(user_id="anna", company_id="muller-ag"),
    "token-keller": CurrentUser(user_id="marco", company_id="keller-gmbh"),
}

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> CurrentUser:
    user = FAKE_TOKENS.get(credentials.credentials) if credentials else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user