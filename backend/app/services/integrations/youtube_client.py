import httpx


class YouTubeClient:
    async def read_channel(self, payload: dict, access_token: str | None = None) -> dict:
        if not access_token:
            return {
                "status": "mock",
                "provider": "youtube",
                "channel_id": payload.get("channel_id"),
                "items": [],
            }

        channel_id = payload.get("channel_id")
        params = {"part": "snippet,statistics", "maxResults": 10}
        if channel_id:
            params["id"] = channel_id
        else:
            params["mine"] = "true"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/channels",
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def upload_video(self, payload: dict, access_token: str | None = None) -> dict:
        if not access_token:
            return {
                "status": "mock",
                "provider": "youtube",
                "title": payload.get("title"),
                "description": payload.get("description"),
            }

        metadata = {
            "snippet": {
                "title": payload.get("title", "Untitled"),
                "description": payload.get("description", ""),
            },
            "status": {"privacyStatus": payload.get("privacy_status", "private")},
        }
        # Full resumable upload requires chunked media transfer; this initializes metadata.
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://www.googleapis.com/upload/youtube/v3/videos",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"part": "snippet,status", "uploadType": "resumable"},
                json=metadata,
            )
            response.raise_for_status()
            return {
                "status": "upload_initialized",
                "provider": "youtube",
                "location": response.headers.get("Location"),
            }


youtube_client = YouTubeClient()
