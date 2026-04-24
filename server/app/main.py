from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover - pydantic v1 compatibility
    ConfigDict = None

from minecraft_coach.module_loader import load_modules

from .storage import (
    BaseBackendStore,
    IDEMPOTENCY_TTL_SECONDS,
    PostgresBackendStore,
    RateLimitExceededError,
    RateLimitRule,
    RemoteStateStore,
    SESSION_TTL_SECONDS,
    json_size_bytes,
    normalize_client_identifier,
    normalize_program_id,
    validate_parent_password_hash,
)


SITE_DIR = ROOT_DIR / "Site"
SITE_ASSETS_DIR = SITE_DIR / "assets"
DIST_DIR = ROOT_DIR / "dist"
MODULES_DIR = ROOT_DIR / "modules"
DATA_DIR = ROOT_DIR / "server" / "data"
SCHEMA_PATH = ROOT_DIR / "server" / "postgresql_schema.sql"
DATABASE_URL = str(os.getenv("MINECRAFT_COACH_DATABASE_URL") or os.getenv("DATABASE_URL") or "").strip()

DEFAULT_ALLOWED_ORIGINS = [
    "https://minecraftcoach.pl",
    "https://www.minecraftcoach.pl",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
MAX_SYNC_PAYLOAD_BYTES = 256 * 1024
IDEMPOTENCY_KEY_MAX_LENGTH = 128
PUBLIC_SITE_FILES = {
    "/",
    "/styles.css",
    "/script.js",
    "/site-config.js",
    "/health",
}


def allowed_origins() -> list[str]:
    raw = str(os.getenv("MINECRAFT_COACH_ALLOWED_ORIGINS") or "").strip()
    if not raw:
        return list(DEFAULT_ALLOWED_ORIGINS)
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_store() -> BaseBackendStore:
    if DATABASE_URL:
        return PostgresBackendStore(
            DATABASE_URL,
            schema_path=SCHEMA_PATH,
            session_ttl_seconds=int(os.getenv("MINECRAFT_COACH_SESSION_TTL_SECONDS") or SESSION_TTL_SECONDS),
            idempotency_ttl_seconds=int(
                os.getenv("MINECRAFT_COACH_IDEMPOTENCY_TTL_SECONDS") or IDEMPOTENCY_TTL_SECONDS
            ),
            violation_threshold=int(os.getenv("MINECRAFT_COACH_RATE_VIOLATION_THRESHOLD") or 5),
            violation_window_seconds=int(
                os.getenv("MINECRAFT_COACH_RATE_VIOLATION_WINDOW_SECONDS") or 15 * 60
            ),
            ban_seconds=int(os.getenv("MINECRAFT_COACH_IP_BAN_SECONDS") or 30 * 60),
        )
    return RemoteStateStore(DATA_DIR / "remote_state.json")


STORE = build_store()

app = FastAPI(title="Minecraft Coach API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
)

if SITE_DIR.exists():
    app.mount("/site-static", StaticFiles(directory=SITE_DIR), name="site-static")
if SITE_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=SITE_ASSETS_DIR), name="site-assets")


@app.middleware("http")
async def apply_backend_protection(request: Request, call_next):
    response_headers = security_headers()
    rate_headers: dict[str, str] = {}
    client_ip = get_client_ip(request)
    if (
        request.url.path not in PUBLIC_SITE_FILES
        and not request.url.path.startswith("/site-static/")
        and not request.url.path.startswith("/assets/")
    ):
        try:
            rate_headers = ensure_rate_limit(request)
        except RateLimitExceededError as exc:
            STORE.log_audit_event(
                "rate_limit_denied",
                ip_address=client_ip,
                success=False,
                details={
                    "path": request.url.path,
                    "retry_after": exc.retry_after,
                    "banned_until": exc.banned_until or "",
                },
            )
            headers = {
                "Retry-After": str(exc.retry_after),
                "X-RateLimit-Limit": str(exc.limit),
                "X-RateLimit-Remaining": "0",
                **response_headers,
            }
            if exc.banned_until:
                headers["X-IP-Banned-Until"] = exc.banned_until
            return JSONResponse({"detail": exc.detail}, status_code=429, headers=headers)
    try:
        response = await call_next(request)
    except HTTPException as exc:  # pragma: no cover - middleware safety net
        headers = dict(exc.headers or {})
        headers.update(response_headers)
        headers.update(rate_headers)
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=headers)
    for key, value in response_headers.items():
        response.headers.setdefault(key, value)
    for key, value in rate_headers.items():
        response.headers.setdefault(key, value)
    return response


def dump_model(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def localized_value(item: dict[str, Any], base: str) -> str:
    for code in ("ru", "pl", "en"):
        value = item.get(f"{base}_{code}")
        if value:
            return str(value)
    return str(item.get(base, ""))


class StrictSchema(BaseModel):
    pass


if ConfigDict is not None:
    StrictSchema.model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
else:
    class _StrictSchemaConfig:
        extra = "forbid"
        anystr_strip_whitespace = True

    StrictSchema.Config = _StrictSchemaConfig


def get_client_ip(request: Request) -> str:
    forwarded_for = str(request.headers.get("x-forwarded-for") or "").strip()
    if forwarded_for:
        first = forwarded_for.split(",", 1)[0].strip()
        if first:
            return first
    if request.client and request.client.host:
        return str(request.client.host)
    return "unknown"


def applicable_rate_limits(path: str) -> list[RateLimitRule]:
    if path.startswith("/auth/login"):
        return [
            RateLimitRule("global_api", 240, 60),
            RateLimitRule("login_burst", 8, 60),
            RateLimitRule("login_window", 30, 900),
        ]
    if path.startswith("/sync/push"):
        return [
            RateLimitRule("global_api", 240, 60),
            RateLimitRule("sync_push_burst", 30, 60),
            RateLimitRule("sync_push_window", 600, 3600),
        ]
    if path.startswith("/sync/pull"):
        return [
            RateLimitRule("global_api", 240, 60),
            RateLimitRule("sync_pull_burst", 20, 60),
        ]
    if path.startswith("/dashboard") or path.startswith("/content"):
        return [
            RateLimitRule("global_api", 240, 60),
            RateLimitRule("session_read_burst", 60, 60),
        ]
    if path.startswith("/downloads/"):
        return [
            RateLimitRule("download_burst", 90, 60),
            RateLimitRule("download_window", 900, 3600),
        ]
    return []


def ensure_rate_limit(request: Request) -> dict[str, str]:
    path = request.url.path
    rules = applicable_rate_limits(path)
    return STORE.enforce_rate_limits(
        ip_address=get_client_ip(request),
        path=path,
        rules=rules,
    )


def security_headers() -> dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "same-origin",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin",
    }


def normalize_sync_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="payload must be an object")
    allowed_sections = {"dashboard", "runtime", "content"}
    unexpected = sorted(set(payload) - allowed_sections)
    if unexpected:
        raise HTTPException(
            status_code=400,
            detail=f"Unexpected payload sections: {', '.join(unexpected)}",
        )
    normalized: dict[str, Any] = {}
    for key in ("dashboard", "runtime", "content"):
        if key not in payload:
            continue
        value = payload.get(key)
        if not isinstance(value, dict):
            raise HTTPException(status_code=400, detail=f"{key} must be an object")
        normalized[key] = value
    if json_size_bytes(normalized) > MAX_SYNC_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail="payload is too large")
    return normalized


def canonical_sync_envelope(payload: "SyncEnvelope") -> dict[str, Any]:
    return {
        "program_id": normalize_program_id(payload.program_id),
        "device_id": normalize_client_identifier("device_id", payload.device_id),
        "checkpoint": normalize_client_identifier("checkpoint", payload.checkpoint),
        "parent_password_hash": validate_parent_password_hash(payload.parent_password_hash),
        "payload": normalize_sync_payload(dump_model(payload).get("payload") or {}),
    }


def sync_fingerprint(payload: "SyncEnvelope") -> str:
    canonical = canonical_sync_envelope(payload)
    return sync_fingerprint_from_canonical(canonical)


def sync_fingerprint_from_canonical(canonical: dict[str, Any]) -> str:
    raw = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validated_idempotency_key(value: str | None) -> str:
    key = str(value or "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    if len(key) > IDEMPOTENCY_KEY_MAX_LENGTH:
        raise HTTPException(status_code=400, detail="Idempotency-Key is too long")
    return key


def require_program_id_from_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    program_id = STORE.resolve_session(token)
    if not program_id:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    return program_id


def current_downloadable_app() -> Path | None:
    preferred = DIST_DIR / "MinecraftCoach.exe"
    if preferred.exists():
        return preferred
    executables = sorted(DIST_DIR.glob("*.exe"), key=lambda path: path.stat().st_mtime, reverse=True)
    return executables[0] if executables else None


def module_catalog() -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    for item in load_modules(MODULES_DIR):
        slug = str(item.get("slug") or item.get("id") or "").strip()
        if not slug:
            continue
        title = localized_value(item, "title") or slug
        description = localized_value(item, "description")
        manifest_path = Path(str(item.get("manifest_path") or ""))
        folder = manifest_path.parent if manifest_path.exists() else MODULES_DIR / slug
        topic_count = len(item.get("topics") or [])
        level_count = len(item.get("levels") or [])
        catalog.append(
            {
                "id": str(item.get("id") or slug),
                "slug": slug,
                "title": title,
                "description": description,
                "topic_count": topic_count,
                "level_count": level_count,
                "download_url": f"/downloads/modules/{slug}.zip",
                "folder": str(folder),
            }
        )
    return catalog


def find_module_folder(slug: str) -> Path | None:
    normalized = str(slug or "").strip()
    for item in module_catalog():
        if item["slug"] == normalized:
            folder = Path(item["folder"])
            if folder.exists():
                return folder
    return None


def site_file_response(filename: str, media_type: str) -> FileResponse:
    file_path = SITE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Site/{filename} was not found")
    return FileResponse(file_path, media_type=media_type)


class LoginRequest(StrictSchema):
    program_id: str = Field(min_length=4, max_length=64)
    parent_password: str = Field(min_length=4, max_length=256)


class SyncEnvelope(StrictSchema):
    program_id: str = Field(min_length=4, max_length=64)
    device_id: str | None = Field(default=None, max_length=128)
    checkpoint: str | None = Field(default=None, max_length=128)
    parent_password_hash: str | None = Field(default=None, max_length=256)
    payload: dict[str, Any] = Field(default_factory=dict)


class TopicUpdate(StrictSchema):
    title_ru: str | None = Field(default=None, max_length=240)
    title_pl: str | None = Field(default=None, max_length=240)
    title_en: str | None = Field(default=None, max_length=240)
    description_ru: str | None = Field(default=None, max_length=4000)
    description_pl: str | None = Field(default=None, max_length=4000)
    description_en: str | None = Field(default=None, max_length=4000)


class TaskUpdate(StrictSchema):
    title_ru: str | None = Field(default=None, max_length=240)
    title_pl: str | None = Field(default=None, max_length=240)
    title_en: str | None = Field(default=None, max_length=240)
    prompt_ru: str | None = Field(default=None, max_length=4000)
    prompt_pl: str | None = Field(default=None, max_length=4000)
    prompt_en: str | None = Field(default=None, max_length=4000)
    accepted_answers: list[str] = Field(default_factory=list, max_length=24)
    options: list[str] = Field(default_factory=list, max_length=24)


class SettingsUpdate(StrictSchema):
    break_seconds: int | None = Field(default=None, ge=30, le=24 * 60 * 60)
    tasks_per_break: int | None = Field(default=None, ge=1, le=50)
    lesson_seconds: int | None = Field(default=None, ge=10, le=24 * 60 * 60)
    window_language: str | None = Field(default=None, max_length=16)
    server_base_url: str | None = Field(default=None, max_length=255)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "has_site": SITE_DIR.exists(),
        "has_app_binary": current_downloadable_app() is not None,
        "module_count": len(module_catalog()),
        "storage": STORE.storage_info(),
    }


@app.get("/downloads/catalog")
def downloads_catalog() -> dict[str, Any]:
    app_file = current_downloadable_app()
    app_payload: dict[str, Any] = {
        "available": False,
        "title": "Minecraft Coach Desktop",
        "download_url": "/downloads/app/latest",
    }
    if app_file:
        stat = app_file.stat()
        app_payload.update(
            {
                "available": True,
                "filename": app_file.name,
                "size_bytes": stat.st_size,
                "updated_at": stat.st_mtime,
            }
        )
    modules = [
        {key: value for key, value in item.items() if key != "folder"}
        for item in module_catalog()
    ]
    return {
        "ok": True,
        "app": app_payload,
        "modules": modules,
        "update_hint": "Replace dist/MinecraftCoach.exe and drop module folders into modules/.",
    }


@app.get("/downloads/app/latest")
def download_latest_app():
    app_file = current_downloadable_app()
    if not app_file:
        raise HTTPException(status_code=404, detail="Application binary was not found in dist/")
    return FileResponse(app_file, filename=app_file.name, media_type="application/octet-stream")


@app.get("/downloads/modules/{slug}.zip")
def download_module(slug: str):
    folder = find_module_folder(slug)
    if not folder:
        raise HTTPException(status_code=404, detail="Module was not found")
    archive_name = f"{slug}.zip"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(path for path in folder.rglob("*") if path.is_file()):
            if "__pycache__" in file_path.parts or file_path.suffix.lower() == ".pyc":
                continue
            archive.write(file_path, arcname=str(Path(slug) / file_path.relative_to(folder)))
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{archive_name}"'},
    )


@app.post("/auth/login")
def login(payload: LoginRequest, request: Request) -> dict[str, Any]:
    client_ip = get_client_ip(request)
    try:
        program_id = normalize_program_id(payload.program_id)
    except ValueError as exc:
        STORE.log_audit_event(
            "auth_login",
            ip_address=client_ip,
            program_id=str(payload.program_id or "").strip().upper(),
            success=False,
            details={"reason": "invalid_program_id"},
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    authenticated = STORE.authenticate(program_id, payload.parent_password)
    STORE.log_audit_event(
        "auth_login",
        ip_address=client_ip,
        program_id=program_id,
        success=authenticated,
        details={"route": "/auth/login"},
    )
    if not authenticated:
        raise HTTPException(status_code=401, detail="Invalid program_id or parent_password")
    session_token = STORE.create_session(program_id, ip_address=client_ip)
    record = STORE.get_program(program_id) or {}
    return {
        "ok": True,
        "session_token": session_token,
        "program_id": program_id,
        "updated_at": record.get("updated_at"),
    }


@app.get("/dashboard")
def dashboard(authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, Any]:
    program_id = require_program_id_from_token(authorization)
    record = STORE.get_program(program_id)
    if not record:
        raise HTTPException(status_code=404, detail="Program snapshot was not found")
    snapshot = dict(record.get("snapshot") or {})
    return {
        "ok": True,
        "program_id": program_id,
        "updated_at": record.get("updated_at"),
        **snapshot,
    }


@app.get("/content")
def content(authorization: str | None = Header(default=None, alias="Authorization")) -> dict[str, Any]:
    program_id = require_program_id_from_token(authorization)
    record = STORE.get_program(program_id)
    if not record:
        raise HTTPException(status_code=404, detail="Program snapshot was not found")
    snapshot = dict(record.get("snapshot") or {})
    return {
        "ok": True,
        "program_id": program_id,
        "content": snapshot.get("content") or {},
        "dashboard": snapshot.get("dashboard") or {},
        "runtime": snapshot.get("runtime") or {},
        "updated_at": record.get("updated_at"),
    }


@app.put("/topics/{topic_id}")
def update_topic(
    topic_id: str,
    payload: TopicUpdate,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, Any]:
    require_program_id_from_token(authorization)
    return {
        "ok": False,
        "message": "Remote editing is not implemented yet.",
        "topic_id": topic_id,
        "payload": dump_model(payload),
    }


@app.put("/tasks/{task_id}")
def update_task(
    task_id: str,
    payload: TaskUpdate,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, Any]:
    require_program_id_from_token(authorization)
    return {
        "ok": False,
        "message": "Remote editing is not implemented yet.",
        "task_id": task_id,
        "payload": dump_model(payload),
    }


@app.put("/settings")
def update_settings(
    payload: SettingsUpdate,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> dict[str, Any]:
    require_program_id_from_token(authorization)
    return {
        "ok": False,
        "message": "Remote settings editing is not implemented yet.",
        "payload": dump_model(payload),
    }


@app.post("/sync/push")
def sync_push(
    payload: SyncEnvelope,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    client_ip = get_client_ip(request)
    key = validated_idempotency_key(idempotency_key)
    try:
        canonical = canonical_sync_envelope(payload)
    except (PermissionError, ValueError) as exc:
        STORE.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=str(payload.program_id or "").strip().upper(),
            success=False,
            details={"reason": str(exc)},
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    fingerprint = sync_fingerprint_from_canonical(canonical)
    state = STORE.begin_idempotent_request(scope="sync_push", key=key, fingerprint=fingerprint)
    if state["state"] == "conflict":
        STORE.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=False,
            details={"reason": "idempotency_conflict"},
        )
        raise HTTPException(
            status_code=409,
            detail="Idempotency-Key was already used for a different payload",
        )
    if state["state"] == "pending":
        STORE.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=False,
            details={"reason": "idempotency_pending"},
        )
        raise HTTPException(
            status_code=409,
            detail="A request with the same Idempotency-Key is already being processed",
        )
    if state["state"] == "replay":
        replay = dict(state.get("response") or {})
        replay["idempotent_replay"] = True
        STORE.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=True,
            details={"reason": "idempotent_replay"},
        )
        return replay

    try:
        record = STORE.upsert_snapshot(
            program_id=canonical["program_id"],
            parent_password_hash=canonical["parent_password_hash"],
            payload=canonical["payload"],
            device_id=canonical["device_id"],
            checkpoint=canonical["checkpoint"],
        )
    except PermissionError as exc:
        STORE.abandon_idempotent_request(scope="sync_push", key=key)
        STORE.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=False,
            details={"reason": str(exc)},
        )
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        STORE.abandon_idempotent_request(scope="sync_push", key=key)
        STORE.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=False,
            details={"reason": str(exc)},
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    response_payload = {
        "ok": True,
        "program_id": record["program_id"],
        "updated_at": record["updated_at"],
    }
    STORE.commit_idempotent_request(
        scope="sync_push",
        key=key,
        fingerprint=fingerprint,
        response=response_payload,
    )
    STORE.log_audit_event(
        "sync_push",
        ip_address=client_ip,
        program_id=canonical["program_id"],
        success=True,
        details={"device_id": canonical["device_id"], "checkpoint": canonical["checkpoint"]},
    )
    return response_payload


@app.post("/sync/pull")
def sync_pull(payload: SyncEnvelope, request: Request) -> dict[str, Any]:
    client_ip = get_client_ip(request)
    try:
        program_id = normalize_program_id(payload.program_id)
        parent_hash = validate_parent_password_hash(payload.parent_password_hash)
    except (PermissionError, ValueError) as exc:
        STORE.log_audit_event(
            "sync_pull",
            ip_address=client_ip,
            program_id=str(payload.program_id or "").strip().upper(),
            success=False,
            details={"reason": str(exc)},
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not STORE.verify_hash(program_id, parent_hash):
        STORE.log_audit_event(
            "sync_pull",
            ip_address=client_ip,
            program_id=program_id,
            success=False,
            details={"reason": "hash_mismatch"},
        )
        raise HTTPException(status_code=403, detail="parent_password_hash does not match the stored hash")
    record = STORE.get_program(program_id)
    if not record:
        STORE.log_audit_event(
            "sync_pull",
            ip_address=client_ip,
            program_id=program_id,
            success=False,
            details={"reason": "program_not_found"},
        )
        raise HTTPException(status_code=404, detail="Program snapshot was not found")
    stored_snapshot = dict(record.get("snapshot") or {})
    STORE.log_audit_event(
        "sync_pull",
        ip_address=client_ip,
        program_id=program_id,
        success=True,
        details={"route": "/sync/pull"},
    )
    return {
        "ok": True,
        "program_id": record["program_id"],
        "updated_at": record.get("updated_at"),
        "payload": stored_snapshot,
    }


@app.get("/")
def site_index():
    index_path = SITE_DIR / "index.html"
    if not index_path.exists():
        return JSONResponse(
            {
                "ok": False,
                "message": "Site/index.html was not found. Place the website files into the Site/ folder.",
            },
            status_code=404,
        )
    return FileResponse(index_path)


@app.get("/styles.css")
def site_styles():
    return site_file_response("styles.css", "text/css; charset=utf-8")


@app.get("/script.js")
def site_script():
    return site_file_response("script.js", "application/javascript; charset=utf-8")


@app.get("/site-config.js")
def site_config():
    config_path = SITE_DIR / "site-config.js"
    if config_path.exists():
        return FileResponse(config_path, media_type="application/javascript; charset=utf-8")
    return Response(
        'window.MinecraftCoachSiteConfig = { apiBaseUrl: "" };',
        media_type="application/javascript; charset=utf-8",
    )
