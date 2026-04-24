from __future__ import annotations

import hashlib
import json
from typing import Any
from urllib import error, request


def build_endpoint(base_url: str, path: str) -> str:
    base = str(base_url or "").strip().rstrip("/")
    if not base:
        raise ValueError("base_url is required")
    if base.endswith(path):
        return base
    return f"{base}{path}"


def push_remote_snapshot(
    *,
    base_url: str,
    program_id: str,
    parent_password_hash: str,
    payload: dict[str, Any],
    device_id: str = "desktop-v23",
    checkpoint: str | None = None,
    timeout: float = 8.0,
) -> dict[str, Any]:
    endpoint = build_endpoint(base_url, "/sync/push")
    envelope = {
        "program_id": str(program_id or "").strip().upper(),
        "device_id": device_id,
        "checkpoint": checkpoint or "",
        "parent_password_hash": str(parent_password_hash or "").strip(),
        "payload": payload or {},
    }
    body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    idempotency_key = hashlib.sha256(body).hexdigest()
    req = request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Idempotency-Key": idempotency_key,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"ok": False, "status": exc.code, "detail": raw}
        payload.setdefault("ok", False)
        payload.setdefault("status", exc.code)
        return payload
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}

    try:
        payload = json.loads(raw) if raw else {}
    except Exception:
        payload = {"ok": True, "raw": raw}
    payload.setdefault("ok", True)
    return payload
