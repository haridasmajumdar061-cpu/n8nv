import base64

import httpx


class GmailClient:
    async def send_email(self, payload: dict, access_token: str | None = None) -> dict:
        if not access_token:
            return {
                "status": "mock",
                "provider": "gmail",
                "to": payload.get("to"),
                "subject": payload.get("subject"),
            }

        to = payload.get("to")
        subject = payload.get("subject", "")
        body = payload.get("body", "")
        mime = f"To: {to}\r\nSubject: {subject}\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n{body}"
        encoded = base64.urlsafe_b64encode(mime.encode("utf-8")).decode("utf-8")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"raw": encoded},
            )
            response.raise_for_status()
            return response.json()

    async def read_inbox(self, payload: dict, access_token: str | None = None) -> dict:
        if not access_token:
            return {"status": "mock", "provider": "gmail", "messages": [], "query": payload.get("query", "")}

        query = payload.get("query", "is:unread")
        max_results = int(payload.get("max_results", 10))

        async with httpx.AsyncClient(timeout=30) as client:
            list_response = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"q": query, "maxResults": max_results},
            )
            list_response.raise_for_status()
            list_data = list_response.json()
            messages = list_data.get("messages", [])

            details = []
            for item in messages:
                msg_id = item.get("id")
                if not msg_id:
                    continue
                msg_response = await client.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"format": "metadata"},
                )
                msg_response.raise_for_status()
                details.append(msg_response.json())

        return {"status": "ok", "provider": "gmail", "messages": details}


gmail_client = GmailClient()
