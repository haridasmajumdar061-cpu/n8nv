from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.integration_credential import IntegrationCredential
from app.utils.oauth_state import encode_oauth_state

GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

PROVIDER_SCOPES = {
    "gmail": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
    ],
    "youtube": [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.upload",
    ],
}


class GoogleOAuthService:
    def build_auth_url(self, provider: str, user_id: int) -> str:
        scopes = PROVIDER_SCOPES.get(provider, [])
        state = encode_oauth_state(provider, user_id, settings.secret_key)
        params = {
            "client_id": settings.gmail_client_id,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "scope": " ".join(scopes),
            "state": state,
        }
        return f"{GOOGLE_AUTH_BASE}?{urlencode(params)}"

    async def exchange_code(
        self,
        db: AsyncSession,
        user_id: int,
        provider: str,
        code: str,
    ) -> dict:
        payload = {
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.google_oauth_redirect_uri,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=payload)
            response.raise_for_status()
            token_data = response.json()

        await self._upsert_credential(db, user_id, provider, token_data)
        return {"status": "connected", "provider": provider}

    async def get_valid_access_token(self, db: AsyncSession, user_id: int, provider: str) -> str | None:
        result = await db.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.user_id == user_id,
                IntegrationCredential.provider == provider,
            )
        )
        cred = result.scalar_one_or_none()
        if not cred:
            return None

        if cred.expires_at and cred.expires_at <= datetime.now(UTC) and cred.refresh_token:
            refreshed = await self._refresh_token(cred.refresh_token)
            await self._upsert_credential(db, user_id, provider, refreshed, existing=cred)
            return refreshed["access_token"]

        return cred.access_token

    async def _refresh_token(self, refresh_token: str) -> dict:
        payload = {
            "client_id": settings.gmail_client_id,
            "client_secret": settings.gmail_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=payload)
            response.raise_for_status()
            return response.json()

    async def _upsert_credential(
        self,
        db: AsyncSession,
        user_id: int,
        provider: str,
        token_data: dict,
        existing: IntegrationCredential | None = None,
    ) -> None:
        expires_at = None
        if token_data.get("expires_in"):
            expires_at = datetime.now(UTC) + timedelta(seconds=int(token_data["expires_in"]))

        cred = existing
        if not cred:
            result = await db.execute(
                select(IntegrationCredential).where(
                    IntegrationCredential.user_id == user_id,
                    IntegrationCredential.provider == provider,
                )
            )
            cred = result.scalar_one_or_none()

        if not cred:
            cred = IntegrationCredential(
                user_id=user_id,
                provider=provider,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_type=token_data.get("token_type", "Bearer"),
                scope=token_data.get("scope"),
                expires_at=expires_at,
                provider_meta={"raw": token_data},
            )
            db.add(cred)
        else:
            cred.access_token = token_data.get("access_token", cred.access_token)
            cred.refresh_token = token_data.get("refresh_token", cred.refresh_token)
            cred.token_type = token_data.get("token_type", cred.token_type)
            cred.scope = token_data.get("scope", cred.scope)
            cred.expires_at = expires_at or cred.expires_at
            cred.provider_meta = {"raw": token_data}

        await db.commit()


google_oauth_service = GoogleOAuthService()
