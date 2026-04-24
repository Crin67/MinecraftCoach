from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import hashlib
import json
import re
import secrets
import threading
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from minecraft_coach.security import is_password_hash, verify_password

try:  # pragma: no cover - optional at import time
    import psycopg
    from psycopg.rows import dict_row
except Exception:  # pragma: no cover - dependency may be missing in some local envs
    psycopg = None
    dict_row = None


SESSION_TTL_SECONDS = 60 * 60 * 8
IDEMPOTENCY_TTL_SECONDS = 60 * 60 * 12
PROGRAM_ID_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{3,63}$")
CLIENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@/-]{0,127}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_program_id(value: str | None) -> str:
    normalized = str(value or "").strip().upper()
    if not PROGRAM_ID_PATTERN.fullmatch(normalized):
        raise ValueError("program_id must contain 4-64 characters: A-Z, 0-9, _ or -")
    return normalized


def normalize_client_identifier(name: str, value: str | None, *, max_length: int = 128) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return ""
    if len(normalized) > max_length:
        raise ValueError(f"{name} is too long")
    if not CLIENT_ID_PATTERN.fullmatch(normalized):
        raise ValueError(f"{name} contains unsupported characters")
    return normalized


def validate_parent_password_hash(value: str | None) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise PermissionError("parent_password_hash is required")
    if not is_password_hash(normalized):
        raise PermissionError("parent_password_hash must be a valid password hash")
    return normalized


def json_size_bytes(payload: Any) -> int:
    return len(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    limit: int
    window_seconds: int


class RateLimitExceededError(Exception):
    def __init__(
        self,
        *,
        retry_after: int,
        limit: int,
        detail: str,
        banned_until: str | None = None,
    ) -> None:
        super().__init__(detail)
        self.retry_after = max(1, int(retry_after))
        self.limit = max(1, int(limit))
        self.detail = detail
        self.banned_until = banned_until


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: dict[str, deque[float]] = {}

    def allow(self, bucket: str, *, limit: int, window_seconds: int) -> dict[str, int | bool]:
        now = time.time()
        with self._lock:
            queue = self._events.setdefault(bucket, deque())
            cutoff = now - window_seconds
            while queue and queue[0] <= cutoff:
                queue.popleft()
            if len(queue) >= limit:
                retry_after = max(1, int(queue[0] + window_seconds - now))
                return {
                    "allowed": False,
                    "limit": limit,
                    "remaining": 0,
                    "retry_after": retry_after,
                }
            queue.append(now)
            remaining = max(0, limit - len(queue))
            return {
                "allowed": True,
                "limit": limit,
                "remaining": remaining,
                "retry_after": 0,
            }


class IdempotencyStore:
    def __init__(self, *, ttl_seconds: int = IDEMPOTENCY_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._records: dict[str, dict[str, Any]] = {}

    def _prune_unlocked(self) -> None:
        cutoff = time.time() - self.ttl_seconds
        expired = [
            key
            for key, row in self._records.items()
            if float(row.get("created_ts", 0.0)) <= cutoff
        ]
        for key in expired:
            self._records.pop(key, None)

    def begin(self, *, scope: str, key: str, fingerprint: str) -> dict[str, Any]:
        compound_key = f"{scope}:{key}"
        with self._lock:
            self._prune_unlocked()
            existing = self._records.get(compound_key)
            if not existing:
                self._records[compound_key] = {
                    "fingerprint": fingerprint,
                    "created_ts": time.time(),
                    "status": "pending",
                }
                return {"state": "started"}
            if str(existing.get("fingerprint") or "") != fingerprint:
                return {"state": "conflict"}
            if existing.get("status") == "done":
                return {"state": "replay", "response": deepcopy(existing.get("response") or {})}
            return {"state": "pending"}

    def commit(self, *, scope: str, key: str, fingerprint: str, response: dict[str, Any]) -> None:
        compound_key = f"{scope}:{key}"
        with self._lock:
            self._records[compound_key] = {
                "fingerprint": fingerprint,
                "created_ts": time.time(),
                "status": "done",
                "response": deepcopy(response or {}),
            }

    def abandon(self, *, scope: str, key: str) -> None:
        compound_key = f"{scope}:{key}"
        with self._lock:
            self._records.pop(compound_key, None)


class BaseBackendStore:
    backend_name = "base"

    def storage_info(self) -> dict[str, Any]:
        return {"backend": self.backend_name}

    def upsert_snapshot(
        self,
        *,
        program_id: str,
        parent_password_hash: str,
        payload: dict[str, Any],
        device_id: str | None = None,
        checkpoint: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def get_program(self, program_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def authenticate(self, program_id: str, parent_password: str) -> bool:
        raise NotImplementedError

    def verify_hash(self, program_id: str, parent_password_hash: str | None) -> bool:
        raise NotImplementedError

    def create_session(self, program_id: str, *, ip_address: str = "") -> str:
        raise NotImplementedError

    def resolve_session(self, token: str | None) -> str | None:
        raise NotImplementedError

    def destroy_session(self, token: str | None) -> None:
        raise NotImplementedError

    def begin_idempotent_request(self, *, scope: str, key: str, fingerprint: str) -> dict[str, Any]:
        raise NotImplementedError

    def commit_idempotent_request(
        self,
        *,
        scope: str,
        key: str,
        fingerprint: str,
        response: dict[str, Any],
    ) -> None:
        raise NotImplementedError

    def abandon_idempotent_request(self, *, scope: str, key: str) -> None:
        raise NotImplementedError

    def enforce_rate_limits(
        self,
        *,
        ip_address: str,
        path: str,
        rules: list[RateLimitRule],
    ) -> dict[str, str]:
        raise NotImplementedError

    def log_audit_event(
        self,
        event_type: str,
        *,
        ip_address: str = "",
        program_id: str = "",
        success: bool = True,
        details: dict[str, Any] | None = None,
    ) -> None:
        raise NotImplementedError


class RemoteStateStore(BaseBackendStore):
    backend_name = "file-json"

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._audit_log_path = self.path.with_name("audit_log.jsonl")
        self._rate_limiter = SlidingWindowRateLimiter()
        self._idempotency = IdempotencyStore()
        self._ip_bans: dict[str, float] = {}
        self._rate_limit_violations: dict[str, deque[float]] = {}
        self.violation_threshold = 5
        self.violation_window_seconds = 15 * 60
        self.ban_seconds = 30 * 60
        if not self.path.exists():
            self._write_unlocked({"programs": {}})

    def storage_info(self) -> dict[str, Any]:
        return {"backend": self.backend_name, "path": str(self.path)}

    def _read_unlocked(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("programs", {})
        return payload

    def _write_unlocked(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _prune_sessions_unlocked(self) -> None:
        now = time.time()
        expired = [token for token, row in self._sessions.items() if float(row.get("expires_at", 0)) <= now]
        for token in expired:
            self._sessions.pop(token, None)

    def _register_rate_limit_violation(self, ip_address: str) -> str | None:
        now = time.time()
        with self._lock:
            queue = self._rate_limit_violations.setdefault(ip_address, deque())
            cutoff = now - self.violation_window_seconds
            while queue and queue[0] <= cutoff:
                queue.popleft()
            queue.append(now)
            if len(queue) >= self.violation_threshold:
                banned_until_ts = now + self.ban_seconds
                self._ip_bans[ip_address] = banned_until_ts
                return datetime.fromtimestamp(banned_until_ts, tz=timezone.utc).replace(
                    microsecond=0
                ).isoformat()
        return None

    def _ensure_not_banned(self, ip_address: str) -> None:
        if not ip_address:
            return
        with self._lock:
            banned_until_ts = float(self._ip_bans.get(ip_address, 0.0))
            if banned_until_ts <= time.time():
                self._ip_bans.pop(ip_address, None)
                return
        retry_after = max(1, int(banned_until_ts - time.time()))
        banned_until = datetime.fromtimestamp(banned_until_ts, tz=timezone.utc).replace(
            microsecond=0
        ).isoformat()
        raise RateLimitExceededError(
            retry_after=retry_after,
            limit=1,
            detail="IP temporarily banned due to repeated rate limit violations.",
            banned_until=banned_until,
        )

    def upsert_snapshot(
        self,
        *,
        program_id: str,
        parent_password_hash: str,
        payload: dict[str, Any],
        device_id: str | None = None,
        checkpoint: str | None = None,
    ) -> dict[str, Any]:
        normalized_program_id = normalize_program_id(program_id)
        normalized_hash = validate_parent_password_hash(parent_password_hash)
        normalized_device_id = normalize_client_identifier("device_id", device_id)
        normalized_checkpoint = normalize_client_identifier("checkpoint", checkpoint)

        with self._lock:
            state = self._read_unlocked()
            programs = state.setdefault("programs", {})
            record = dict(programs.get(normalized_program_id) or {})
            stored_hash = str(record.get("parent_password_hash") or "")
            if stored_hash and stored_hash != normalized_hash:
                raise PermissionError("parent_password_hash does not match the stored hash")

            now = utc_now()
            record["program_id"] = normalized_program_id
            record["parent_password_hash"] = normalized_hash
            record["device_id"] = normalized_device_id or str(record.get("device_id") or "")
            record["checkpoint"] = normalized_checkpoint
            record["updated_at"] = now
            record["snapshot"] = deepcopy(payload or {})
            programs[normalized_program_id] = record
            self._write_unlocked(state)
            return self._public_record(record)

    def get_program(self, program_id: str) -> dict[str, Any] | None:
        try:
            normalized_program_id = normalize_program_id(program_id)
        except ValueError:
            return None
        with self._lock:
            state = self._read_unlocked()
            record = state.get("programs", {}).get(normalized_program_id)
            if not record:
                return None
            return self._public_record(record)

    def authenticate(self, program_id: str, parent_password: str) -> bool:
        try:
            normalized_program_id = normalize_program_id(program_id)
        except ValueError:
            return False
        if not parent_password:
            return False
        with self._lock:
            state = self._read_unlocked()
            record = state.get("programs", {}).get(normalized_program_id)
            if not record:
                return False
            stored_hash = str(record.get("parent_password_hash") or "")
        return verify_password(parent_password, stored_hash)

    def verify_hash(self, program_id: str, parent_password_hash: str | None) -> bool:
        try:
            normalized_program_id = normalize_program_id(program_id)
            candidate_hash = validate_parent_password_hash(parent_password_hash)
        except (PermissionError, ValueError):
            return False
        with self._lock:
            state = self._read_unlocked()
            record = state.get("programs", {}).get(normalized_program_id)
            if not record:
                return False
            stored_hash = str(record.get("parent_password_hash") or "")
        return bool(stored_hash) and secrets.compare_digest(candidate_hash, stored_hash)

    def create_session(self, program_id: str, *, ip_address: str = "") -> str:
        normalized_program_id = normalize_program_id(program_id)
        with self._lock:
            self._prune_sessions_unlocked()
            token = secrets.token_urlsafe(32)
            self._sessions[token] = {
                "program_id": normalized_program_id,
                "ip_address": ip_address,
                "expires_at": time.time() + SESSION_TTL_SECONDS,
            }
            return token

    def resolve_session(self, token: str | None) -> str | None:
        if not token:
            return None
        with self._lock:
            self._prune_sessions_unlocked()
            row = self._sessions.get(token)
            if not row:
                return None
            row["expires_at"] = time.time() + SESSION_TTL_SECONDS
            return str(row.get("program_id") or "")

    def destroy_session(self, token: str | None) -> None:
        if not token:
            return
        with self._lock:
            self._sessions.pop(token, None)

    def begin_idempotent_request(self, *, scope: str, key: str, fingerprint: str) -> dict[str, Any]:
        return self._idempotency.begin(scope=scope, key=key, fingerprint=fingerprint)

    def commit_idempotent_request(
        self,
        *,
        scope: str,
        key: str,
        fingerprint: str,
        response: dict[str, Any],
    ) -> None:
        self._idempotency.commit(scope=scope, key=key, fingerprint=fingerprint, response=response)

    def abandon_idempotent_request(self, *, scope: str, key: str) -> None:
        self._idempotency.abandon(scope=scope, key=key)

    def enforce_rate_limits(
        self,
        *,
        ip_address: str,
        path: str,
        rules: list[RateLimitRule],
    ) -> dict[str, str]:
        self._ensure_not_banned(ip_address)
        primary_limit = 0
        primary_remaining = 0
        for rule in rules:
            result = self._rate_limiter.allow(
                f"{rule.name}:{ip_address}",
                limit=rule.limit,
                window_seconds=rule.window_seconds,
            )
            if not result["allowed"]:
                banned_until = self._register_rate_limit_violation(ip_address)
                raise RateLimitExceededError(
                    retry_after=int(result["retry_after"]),
                    limit=rule.limit,
                    detail=f"Rate limit exceeded for {path}. Please try again later.",
                    banned_until=banned_until,
                )
            if not primary_limit:
                primary_limit = int(result["limit"])
                primary_remaining = int(result["remaining"])
        return {
            "X-RateLimit-Limit": str(primary_limit),
            "X-RateLimit-Remaining": str(primary_remaining),
        }

    def log_audit_event(
        self,
        event_type: str,
        *,
        ip_address: str = "",
        program_id: str = "",
        success: bool = True,
        details: dict[str, Any] | None = None,
    ) -> None:
        row = {
            "created_at": utc_now(),
            "event_type": str(event_type or "").strip(),
            "ip_address": str(ip_address or "").strip(),
            "program_id": str(program_id or "").strip(),
            "success": bool(success),
            "details": details or {},
        }
        try:
            with self._lock:
                with self._audit_log_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _public_record(self, record: dict[str, Any]) -> dict[str, Any]:
        snapshot = deepcopy(record.get("snapshot") or {})
        return {
            "program_id": str(record.get("program_id") or ""),
            "device_id": str(record.get("device_id") or ""),
            "checkpoint": str(record.get("checkpoint") or ""),
            "updated_at": str(record.get("updated_at") or ""),
            "snapshot": snapshot,
        }


class PostgresBackendStore(BaseBackendStore):
    backend_name = "postgresql"

    def __init__(
        self,
        dsn: str,
        *,
        schema_path: Path,
        session_ttl_seconds: int = SESSION_TTL_SECONDS,
        idempotency_ttl_seconds: int = IDEMPOTENCY_TTL_SECONDS,
        violation_threshold: int = 5,
        violation_window_seconds: int = 15 * 60,
        ban_seconds: int = 30 * 60,
        cleanup_interval_seconds: int = 300,
    ) -> None:
        if psycopg is None or dict_row is None:
            raise RuntimeError(
                "psycopg is not installed. Run `pip install -r server/requirements.txt` first."
            )
        self.dsn = str(dsn or "").strip()
        if not self.dsn:
            raise ValueError("dsn is required")
        self.schema_path = Path(schema_path)
        self.session_ttl_seconds = max(60, int(session_ttl_seconds))
        self.idempotency_ttl_seconds = max(60, int(idempotency_ttl_seconds))
        self.violation_threshold = max(2, int(violation_threshold))
        self.violation_window_seconds = max(60, int(violation_window_seconds))
        self.ban_seconds = max(60, int(ban_seconds))
        self.cleanup_interval_seconds = max(60, int(cleanup_interval_seconds))
        self._cleanup_lock = threading.Lock()
        self._last_cleanup_ts = 0.0
        self._ensure_schema()

    def storage_info(self) -> dict[str, Any]:
        return {
            "backend": self.backend_name,
            "database_url_configured": True,
        }

    def connect(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _ensure_schema(self) -> None:
        sql = self.schema_path.read_text(encoding="utf-8")
        with self.connect() as con:
            con.execute(sql)
            con.commit()

    def _maybe_cleanup(self, con) -> None:
        now_ts = time.monotonic()
        if now_ts - self._last_cleanup_ts < self.cleanup_interval_seconds:
            return
        with self._cleanup_lock:
            if now_ts - self._last_cleanup_ts < self.cleanup_interval_seconds:
                return
            con.execute("DELETE FROM remote_sessions WHERE expires_at <= NOW()")
            con.execute("DELETE FROM api_idempotency_keys WHERE expires_at <= NOW()")
            con.execute(
                "DELETE FROM rate_limit_hits WHERE created_at <= NOW() - INTERVAL '2 days'"
            )
            con.execute(
                "DELETE FROM rate_limit_violations WHERE created_at <= NOW() - INTERVAL '7 days'"
            )
            con.execute("DELETE FROM ip_bans WHERE ban_until <= NOW() - INTERVAL '1 day'")
            self._last_cleanup_ts = now_ts

    def _get_snapshot_row(self, con, program_id: str) -> dict[str, Any] | None:
        return con.execute(
            """
            SELECT program_id, parent_password_hash, device_id, checkpoint, snapshot_json, updated_at
            FROM remote_program_snapshots
            WHERE program_id = %s
            """,
            (program_id,),
        ).fetchone()

    def _public_record_from_row(self, row: dict[str, Any] | None) -> dict[str, Any] | None:
        if not row:
            return None
        snapshot = row.get("snapshot_json") or {}
        if not isinstance(snapshot, dict):
            snapshot = {}
        return {
            "program_id": str(row.get("program_id") or ""),
            "device_id": str(row.get("device_id") or ""),
            "checkpoint": str(row.get("checkpoint") or ""),
            "updated_at": (
                row.get("updated_at").replace(microsecond=0).isoformat()
                if row.get("updated_at")
                else ""
            ),
            "snapshot": deepcopy(snapshot),
        }

    def upsert_snapshot(
        self,
        *,
        program_id: str,
        parent_password_hash: str,
        payload: dict[str, Any],
        device_id: str | None = None,
        checkpoint: str | None = None,
    ) -> dict[str, Any]:
        normalized_program_id = normalize_program_id(program_id)
        normalized_hash = validate_parent_password_hash(parent_password_hash)
        normalized_device_id = normalize_client_identifier("device_id", device_id)
        normalized_checkpoint = normalize_client_identifier("checkpoint", checkpoint)
        with self.connect() as con:
            self._maybe_cleanup(con)
            existing = con.execute(
                """
                SELECT parent_password_hash
                FROM remote_program_snapshots
                WHERE program_id = %s
                FOR UPDATE
                """,
                (normalized_program_id,),
            ).fetchone()
            stored_hash = str((existing or {}).get("parent_password_hash") or "")
            if stored_hash and stored_hash != normalized_hash:
                raise PermissionError("parent_password_hash does not match the stored hash")
            con.execute(
                """
                INSERT INTO remote_program_snapshots(
                    program_id,
                    parent_password_hash,
                    device_id,
                    checkpoint,
                    snapshot_json,
                    created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW(), NOW())
                ON CONFLICT (program_id) DO UPDATE SET
                    parent_password_hash = EXCLUDED.parent_password_hash,
                    device_id = CASE
                        WHEN EXCLUDED.device_id <> '' THEN EXCLUDED.device_id
                        ELSE remote_program_snapshots.device_id
                    END,
                    checkpoint = EXCLUDED.checkpoint,
                    snapshot_json = EXCLUDED.snapshot_json,
                    updated_at = NOW()
                """,
                (
                    normalized_program_id,
                    normalized_hash,
                    normalized_device_id,
                    normalized_checkpoint,
                    json.dumps(payload or {}, ensure_ascii=False),
                ),
            )
            row = self._get_snapshot_row(con, normalized_program_id)
            con.commit()
        return self._public_record_from_row(row) or {
            "program_id": normalized_program_id,
            "device_id": normalized_device_id,
            "checkpoint": normalized_checkpoint,
            "updated_at": utc_now(),
            "snapshot": deepcopy(payload or {}),
        }

    def get_program(self, program_id: str) -> dict[str, Any] | None:
        try:
            normalized_program_id = normalize_program_id(program_id)
        except ValueError:
            return None
        with self.connect() as con:
            row = self._get_snapshot_row(con, normalized_program_id)
        return self._public_record_from_row(row)

    def authenticate(self, program_id: str, parent_password: str) -> bool:
        try:
            normalized_program_id = normalize_program_id(program_id)
        except ValueError:
            return False
        if not parent_password:
            return False
        with self.connect() as con:
            row = con.execute(
                """
                SELECT parent_password_hash
                FROM remote_program_snapshots
                WHERE program_id = %s
                """,
                (normalized_program_id,),
            ).fetchone()
        stored_hash = str((row or {}).get("parent_password_hash") or "")
        return verify_password(parent_password, stored_hash)

    def verify_hash(self, program_id: str, parent_password_hash: str | None) -> bool:
        try:
            normalized_program_id = normalize_program_id(program_id)
            candidate_hash = validate_parent_password_hash(parent_password_hash)
        except (PermissionError, ValueError):
            return False
        with self.connect() as con:
            row = con.execute(
                """
                SELECT parent_password_hash
                FROM remote_program_snapshots
                WHERE program_id = %s
                """,
                (normalized_program_id,),
            ).fetchone()
        stored_hash = str((row or {}).get("parent_password_hash") or "")
        return bool(stored_hash) and secrets.compare_digest(candidate_hash, stored_hash)

    def create_session(self, program_id: str, *, ip_address: str = "") -> str:
        normalized_program_id = normalize_program_id(program_id)
        token = secrets.token_urlsafe(32)
        token_hash = sha256_text(token)
        with self.connect() as con:
            self._maybe_cleanup(con)
            con.execute(
                """
                INSERT INTO remote_sessions(
                    token_hash,
                    program_id,
                    ip_address,
                    created_at,
                    last_seen_at,
                    expires_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    NOW(),
                    NOW(),
                    NOW() + make_interval(secs => %s)
                )
                """,
                (token_hash, normalized_program_id, str(ip_address or "").strip(), self.session_ttl_seconds),
            )
            con.commit()
        return token

    def resolve_session(self, token: str | None) -> str | None:
        if not token:
            return None
        token_hash = sha256_text(token)
        with self.connect() as con:
            self._maybe_cleanup(con)
            row = con.execute(
                """
                UPDATE remote_sessions
                SET
                    last_seen_at = NOW(),
                    expires_at = NOW() + make_interval(secs => %s)
                WHERE token_hash = %s
                  AND expires_at > NOW()
                RETURNING program_id
                """,
                (self.session_ttl_seconds, token_hash),
            ).fetchone()
            con.commit()
        return str((row or {}).get("program_id") or "") or None

    def destroy_session(self, token: str | None) -> None:
        if not token:
            return
        token_hash = sha256_text(token)
        with self.connect() as con:
            con.execute("DELETE FROM remote_sessions WHERE token_hash = %s", (token_hash,))
            con.commit()

    def begin_idempotent_request(self, *, scope: str, key: str, fingerprint: str) -> dict[str, Any]:
        with self.connect() as con:
            self._maybe_cleanup(con)
            inserted = con.execute(
                """
                INSERT INTO api_idempotency_keys(
                    scope,
                    key,
                    fingerprint,
                    status,
                    response_json,
                    created_at,
                    updated_at,
                    expires_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    'pending',
                    '{}'::jsonb,
                    NOW(),
                    NOW(),
                    NOW() + make_interval(secs => %s)
                )
                ON CONFLICT (scope, key) DO NOTHING
                RETURNING scope
                """,
                (scope, key, fingerprint, self.idempotency_ttl_seconds),
            ).fetchone()
            if inserted:
                con.commit()
                return {"state": "started"}
            row = con.execute(
                """
                SELECT fingerprint, status, response_json
                FROM api_idempotency_keys
                WHERE scope = %s
                  AND key = %s
                  AND expires_at > NOW()
                """,
                (scope, key),
            ).fetchone()
            if not row:
                con.execute(
                    """
                    INSERT INTO api_idempotency_keys(
                        scope,
                        key,
                        fingerprint,
                        status,
                        response_json,
                        created_at,
                        updated_at,
                        expires_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        'pending',
                        '{}'::jsonb,
                        NOW(),
                        NOW(),
                        NOW() + make_interval(secs => %s)
                    )
                    ON CONFLICT (scope, key) DO NOTHING
                    """,
                    (scope, key, fingerprint, self.idempotency_ttl_seconds),
                )
                con.commit()
                return {"state": "started"}
            con.commit()
        if str(row.get("fingerprint") or "") != fingerprint:
            return {"state": "conflict"}
        if str(row.get("status") or "") == "done":
            response = row.get("response_json") or {}
            if not isinstance(response, dict):
                response = {}
            return {"state": "replay", "response": response}
        return {"state": "pending"}

    def commit_idempotent_request(
        self,
        *,
        scope: str,
        key: str,
        fingerprint: str,
        response: dict[str, Any],
    ) -> None:
        with self.connect() as con:
            con.execute(
                """
                UPDATE api_idempotency_keys
                SET
                    fingerprint = %s,
                    status = 'done',
                    response_json = %s::jsonb,
                    updated_at = NOW(),
                    expires_at = NOW() + make_interval(secs => %s)
                WHERE scope = %s
                  AND key = %s
                """,
                (
                    fingerprint,
                    json.dumps(response or {}, ensure_ascii=False),
                    self.idempotency_ttl_seconds,
                    scope,
                    key,
                ),
            )
            con.commit()

    def abandon_idempotent_request(self, *, scope: str, key: str) -> None:
        with self.connect() as con:
            con.execute(
                """
                DELETE FROM api_idempotency_keys
                WHERE scope = %s
                  AND key = %s
                  AND status = 'pending'
                """,
                (scope, key),
            )
            con.commit()

    def _ban_ip_if_needed(self, con, ip_address: str, *, bucket: str, route: str, limit: int) -> str | None:
        violation_total = con.execute(
            """
            SELECT COUNT(*) AS total
            FROM rate_limit_violations
            WHERE ip_address = %s
              AND created_at > NOW() - make_interval(secs => %s)
            """,
            (ip_address, self.violation_window_seconds),
        ).fetchone()
        total = int((violation_total or {}).get("total") or 0)
        if total < self.violation_threshold:
            return None
        row = con.execute(
            """
            INSERT INTO ip_bans(
                ip_address,
                reason,
                ban_until,
                details_json,
                created_at,
                updated_at
            )
            VALUES (
                %s,
                %s,
                NOW() + make_interval(secs => %s),
                %s::jsonb,
                NOW(),
                NOW()
            )
            ON CONFLICT (ip_address) DO UPDATE SET
                reason = EXCLUDED.reason,
                ban_until = GREATEST(ip_bans.ban_until, EXCLUDED.ban_until),
                details_json = EXCLUDED.details_json,
                updated_at = NOW()
            RETURNING ban_until
            """,
            (
                ip_address,
                "Repeated rate limit violations",
                self.ban_seconds,
                json.dumps(
                    {
                        "bucket": bucket,
                        "route": route,
                        "limit": limit,
                        "violation_threshold": self.violation_threshold,
                    },
                    ensure_ascii=False,
                ),
            ),
        ).fetchone()
        banned_until = row.get("ban_until") if row else None
        if banned_until:
            return banned_until.replace(microsecond=0).isoformat()
        return None

    def enforce_rate_limits(
        self,
        *,
        ip_address: str,
        path: str,
        rules: list[RateLimitRule],
    ) -> dict[str, str]:
        primary_limit = 0
        primary_remaining = 0
        normalized_ip = str(ip_address or "").strip() or "unknown"
        with self.connect() as con:
            self._maybe_cleanup(con)
            ban_row = con.execute(
                """
                SELECT ban_until
                FROM ip_bans
                WHERE ip_address = %s
                  AND ban_until > NOW()
                """,
                (normalized_ip,),
            ).fetchone()
            if ban_row:
                banned_until = ban_row["ban_until"].replace(microsecond=0).isoformat()
                retry_after = max(
                    1,
                    int((ban_row["ban_until"] - datetime.now(timezone.utc)).total_seconds()),
                )
                raise RateLimitExceededError(
                    retry_after=retry_after,
                    limit=1,
                    detail="IP temporarily banned due to repeated rate limit violations.",
                    banned_until=banned_until,
                )

            for rule in rules:
                lock_key = f"{rule.name}:{normalized_ip}"
                con.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (lock_key,))
                count_row = con.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM rate_limit_hits
                    WHERE ip_address = %s
                      AND bucket = %s
                      AND created_at > NOW() - make_interval(secs => %s)
                    """,
                    (normalized_ip, rule.name, rule.window_seconds),
                ).fetchone()
                total = int((count_row or {}).get("total") or 0)
                if total >= rule.limit:
                    con.execute(
                        """
                        INSERT INTO rate_limit_violations(
                            ip_address,
                            bucket,
                            route,
                            details_json,
                            created_at
                        )
                        VALUES (%s, %s, %s, %s::jsonb, NOW())
                        """,
                        (
                            normalized_ip,
                            rule.name,
                            path,
                            json.dumps(
                                {
                                    "limit": rule.limit,
                                    "window_seconds": rule.window_seconds,
                                },
                                ensure_ascii=False,
                            ),
                        ),
                    )
                    banned_until = self._ban_ip_if_needed(
                        con,
                        normalized_ip,
                        bucket=rule.name,
                        route=path,
                        limit=rule.limit,
                    )
                    con.commit()
                    raise RateLimitExceededError(
                        retry_after=rule.window_seconds,
                        limit=rule.limit,
                        detail=f"Rate limit exceeded for {path}. Please try again later.",
                        banned_until=banned_until,
                    )
                con.execute(
                    """
                    INSERT INTO rate_limit_hits(ip_address, bucket, route, created_at)
                    VALUES (%s, %s, %s, NOW())
                    """,
                    (normalized_ip, rule.name, path),
                )
                if not primary_limit:
                    primary_limit = rule.limit
                    primary_remaining = max(0, rule.limit - total - 1)
            con.commit()
        return {
            "X-RateLimit-Limit": str(primary_limit),
            "X-RateLimit-Remaining": str(primary_remaining),
        }

    def log_audit_event(
        self,
        event_type: str,
        *,
        ip_address: str = "",
        program_id: str = "",
        success: bool = True,
        details: dict[str, Any] | None = None,
    ) -> None:
        with self.connect() as con:
            con.execute(
                """
                INSERT INTO backend_audit_log(
                    event_type,
                    ip_address,
                    program_id,
                    success,
                    details_json,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW())
                """,
                (
                    str(event_type or "").strip(),
                    str(ip_address or "").strip(),
                    str(program_id or "").strip(),
                    bool(success),
                    json.dumps(details or {}, ensure_ascii=False),
                ),
            )
            con.commit()
