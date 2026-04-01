from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_credentials(client_secrets_path: Path, token_path: Path):
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _load_credentials(token_path: Path):
    from google.oauth2.credentials import Credentials

    data = json.loads(token_path.read_text(encoding="utf-8"))
    return Credentials.from_authorized_user_info(data, SCOPES)


def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "27",
    privacy_status: str = "private",
    thumbnail_path: Path | None = None,
    client_secrets_path: Path | None = None,
    token_path: Path | None = None,
) -> dict[str, Any]:
    client_secrets_path = client_secrets_path or Path("client_secrets.json")
    token_path = token_path or Path("token.json")

    if token_path.exists():
        creds = _load_credentials(token_path)
    else:
        creds = _get_credentials(client_secrets_path, token_path)

    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {"privacyStatus": privacy_status},
        },
        media_body=MediaFileUpload(str(video_path), resumable=True),
    )

    response = request.execute()

    if thumbnail_path and thumbnail_path.exists():
        youtube.thumbnails().set(
            videoId=response["id"],
            media_body=MediaFileUpload(str(thumbnail_path)),
        ).execute()

    return response
