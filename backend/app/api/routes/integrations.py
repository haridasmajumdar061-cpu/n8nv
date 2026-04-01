from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.integration import OAuthCodeExchangeRequest, OAuthURLRequest
from app.services.integrations.gmail_client import gmail_client
from app.services.integrations.google_oauth import google_oauth_service
from app.services.integrations.telegram_client import telegram_client
from app.services.integrations.youtube_client import youtube_client
from app.utils.oauth_state import decode_oauth_state

router = APIRouter()


@router.post("/google/oauth-url")
async def google_oauth_url(
    payload: OAuthURLRequest,
    user: User = Depends(get_current_active_user),
) -> dict:
    if payload.provider not in {"gmail", "youtube"}:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    return {"url": google_oauth_service.build_auth_url(payload.provider, user.id)}


@router.post("/google/exchange-code")
async def google_exchange_code(
    payload: OAuthCodeExchangeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> dict:
    if payload.provider not in {"gmail", "youtube"}:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    if payload.state:
        try:
            state_provider, state_user_id = decode_oauth_state(payload.state, settings.secret_key)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid OAuth state") from exc
        if state_provider != payload.provider or state_user_id != user.id:
            raise HTTPException(status_code=400, detail="OAuth state mismatch")
    return await google_oauth_service.exchange_code(db, user.id, payload.provider, payload.code)


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    try:
        provider, user_id = decode_oauth_state(state, settings.secret_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid OAuth state") from exc

    if provider not in {"gmail", "youtube"}:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    result = await google_oauth_service.exchange_code(db, user_id, provider, code)
    return JSONResponse(result)


@router.post("/gmail/send")
async def gmail_send(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> dict:
    token = await google_oauth_service.get_valid_access_token(db, user.id, "gmail")
    return await gmail_client.send_email(payload, token)


@router.post("/gmail/read")
async def gmail_read(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> dict:
    token = await google_oauth_service.get_valid_access_token(db, user.id, "gmail")
    return await gmail_client.read_inbox(payload, token)


@router.post("/telegram/send")
async def telegram_send(payload: dict, _: User = Depends(get_current_active_user)) -> dict:
    return await telegram_client.send_message(payload)


@router.post("/youtube/read")
async def youtube_read(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> dict:
    token = await google_oauth_service.get_valid_access_token(db, user.id, "youtube")
    return await youtube_client.read_channel(payload, token)


@router.post("/youtube/upload")
async def youtube_upload(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
) -> dict:
    token = await google_oauth_service.get_valid_access_token(db, user.id, "youtube")
    return await youtube_client.upload_video(payload, token)
