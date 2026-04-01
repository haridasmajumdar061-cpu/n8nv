#!/usr/bin/env python3
"""End-to-end smoke test for AI Life OS API."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.getenv("SMOKE_BASE_URL", "http://localhost:8000/api")
EMAIL = os.getenv("SMOKE_EMAIL", "smoke@example.com")
PASSWORD = os.getenv("SMOKE_PASSWORD", "SmokePass123!")


def _request(method: str, path: str, payload: dict | None = None, token: str | None = None) -> dict:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _get_token() -> tuple[str, str]:
    try:
        data = _request(
            "POST",
            "/auth/signup",
            {"email": EMAIL, "password": PASSWORD, "full_name": "Smoke User"},
        )
        return data["access_token"], "signup"
    except urllib.error.HTTPError as exc:
        if exc.code != 409:
            raise
        data = _request("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})
        return data["access_token"], "login"


def main() -> int:
    # Wait for API readiness to avoid startup race failures.
    health_url = BASE_URL[:-4] + "/health" if BASE_URL.endswith("/api") else BASE_URL + "/health"
    for _ in range(40):
        try:
            with urllib.request.urlopen(health_url, timeout=10):
                pass
            break
        except Exception:
            time.sleep(1)

    token, auth_mode = _get_token()

    workflow = _request(
        "POST",
        "/workflows",
        {
            "name": "CI Smoke Workflow",
            "description": "Verifies workflow execution path",
            "is_active": True,
            "definition": {
                "nodes": [
                    {"id": "1", "type": "trigger", "config": {"trigger": "manual"}},
                    {"id": "2", "type": "ai", "config": {"task": "Summarize smoke test"}},
                    {"id": "3", "type": "action", "config": {"provider": "telegram", "text": "done"}},
                ],
                "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
            },
        },
        token=token,
    )

    execution = _request(
        "POST",
        "/executions/run",
        {"workflow_id": workflow["id"], "input_payload": {"source": "smoke"}},
        token=token,
    )
    execution_id = execution["id"]

    status = "queued"
    for _ in range(20):
        details = _request("GET", f"/executions/{execution_id}", token=token)
        status = details["status"]
        if status in {"success", "failed"}:
            break
        time.sleep(1)

    logs = _request("GET", f"/executions/{execution_id}/logs", token=token)

    result = {
        "auth_mode": auth_mode,
        "workflow_id": workflow["id"],
        "execution_id": execution_id,
        "status": status,
        "logs_count": len(logs),
    }
    print(json.dumps(result, indent=2))

    if status != "success":
        print("Smoke test failed: execution did not succeed", file=sys.stderr)
        return 1
    if len(logs) == 0:
        print("Smoke test failed: execution logs are empty", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
