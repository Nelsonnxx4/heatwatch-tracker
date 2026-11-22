import secrets

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings


async def require_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_api_key is not None and any(
        secrets.compare_digest(x_api_key, key) for key in settings.api_key_list
    ):
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key",
        headers={"WWW-Authenticate": "ApiKey"},
    )
