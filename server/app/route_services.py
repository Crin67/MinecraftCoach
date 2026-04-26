from __future__ import annotations

from pathlib import Path
from typing import Any

from .storage import BaseBackendStore, normalize_program_id, validate_parent_password_hash


class IdempotencyConflictError(RuntimeError):
    pass


class IdempotencyPendingError(RuntimeError):
    pass


def build_health_payload(
    *,
    has_site: bool,
    has_app_binary: bool,
    module_count: int,
    storage_info: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "ok",
        "has_site": has_site,
        "has_app_binary": has_app_binary,
        "module_count": module_count,
        "storage": storage_info,
    }


def build_downloads_catalog_payload(app_file: Path | None, modules: list[dict[str, Any]]) -> dict[str, Any]:
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
    return {
        "ok": True,
        "app": app_payload,
        "modules": modules,
        "update_hint": "Replace dist/MinecraftCoach.exe and drop module folders into modules/.",
    }


def authenticate_login(
    store: BaseBackendStore,
    *,
    program_id: str,
    parent_password: str,
    client_ip: str,
) -> dict[str, Any]:
    try:
        normalized_program_id = normalize_program_id(program_id)
    except ValueError as exc:
        store.log_audit_event(
            "auth_login",
            ip_address=client_ip,
            program_id=str(program_id or "").strip().upper(),
            success=False,
            details={"reason": "invalid_program_id"},
        )
        raise

    authenticated = store.authenticate(normalized_program_id, parent_password)
    store.log_audit_event(
        "auth_login",
        ip_address=client_ip,
        program_id=normalized_program_id,
        success=authenticated,
        details={"route": "/auth/login"},
    )
    if not authenticated:
        raise PermissionError("Invalid program_id or parent_password")

    session_token = store.create_session(normalized_program_id, ip_address=client_ip)
    record = store.get_program(normalized_program_id) or {}
    return {
        "ok": True,
        "session_token": session_token,
        "program_id": normalized_program_id,
        "updated_at": record.get("updated_at"),
    }


def get_program_record(store: BaseBackendStore, program_id: str) -> dict[str, Any]:
    record = store.get_program(program_id)
    if not record:
        raise LookupError("Program snapshot was not found")
    return record


def build_dashboard_payload(program_id: str, record: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(record.get("snapshot") or {})
    return {
        "ok": True,
        "program_id": program_id,
        "updated_at": record.get("updated_at"),
        **snapshot,
    }


def build_content_payload(program_id: str, record: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(record.get("snapshot") or {})
    return {
        "ok": True,
        "program_id": program_id,
        "content": snapshot.get("content") or {},
        "dashboard": snapshot.get("dashboard") or {},
        "runtime": snapshot.get("runtime") or {},
        "updated_at": record.get("updated_at"),
    }


def build_placeholder_update_payload(
    *,
    key: str,
    identifier: str | None = None,
    payload: dict[str, Any],
    message: str,
) -> dict[str, Any]:
    response = {
        "ok": False,
        "message": message,
        "payload": payload,
    }
    if identifier is not None:
        response[key] = identifier
    return response


def handle_sync_push(
    store: BaseBackendStore,
    *,
    canonical: dict[str, Any],
    key: str,
    fingerprint: str,
    client_ip: str,
) -> dict[str, Any]:
    state = store.begin_idempotent_request(scope="sync_push", key=key, fingerprint=fingerprint)
    if state["state"] == "conflict":
        store.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=False,
            details={"reason": "idempotency_conflict"},
        )
        raise IdempotencyConflictError("Idempotency-Key was already used for a different payload")
    if state["state"] == "pending":
        store.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=False,
            details={"reason": "idempotency_pending"},
        )
        raise IdempotencyPendingError("A request with the same Idempotency-Key is already being processed")
    if state["state"] == "replay":
        replay = dict(state.get("response") or {})
        replay["idempotent_replay"] = True
        store.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=True,
            details={"reason": "idempotent_replay"},
        )
        return replay

    try:
        record = store.upsert_snapshot(
            program_id=canonical["program_id"],
            parent_password_hash=canonical["parent_password_hash"],
            payload=canonical["payload"],
            device_id=canonical["device_id"],
            checkpoint=canonical["checkpoint"],
        )
    except (PermissionError, ValueError) as exc:
        store.abandon_idempotent_request(scope="sync_push", key=key)
        store.log_audit_event(
            "sync_push",
            ip_address=client_ip,
            program_id=canonical["program_id"],
            success=False,
            details={"reason": str(exc)},
        )
        raise

    response_payload = {
        "ok": True,
        "program_id": record["program_id"],
        "updated_at": record["updated_at"],
    }
    store.commit_idempotent_request(
        scope="sync_push",
        key=key,
        fingerprint=fingerprint,
        response=response_payload,
    )
    store.log_audit_event(
        "sync_push",
        ip_address=client_ip,
        program_id=canonical["program_id"],
        success=True,
        details={"device_id": canonical["device_id"], "checkpoint": canonical["checkpoint"]},
    )
    return response_payload


def handle_sync_pull(
    store: BaseBackendStore,
    *,
    payload_program_id: str,
    payload_parent_password_hash: str | None,
    client_ip: str,
) -> dict[str, Any]:
    try:
        program_id = normalize_program_id(payload_program_id)
        parent_hash = validate_parent_password_hash(payload_parent_password_hash)
    except (PermissionError, ValueError) as exc:
        store.log_audit_event(
            "sync_pull",
            ip_address=client_ip,
            program_id=str(payload_program_id or "").strip().upper(),
            success=False,
            details={"reason": str(exc)},
        )
        raise ValueError(str(exc)) from exc

    if not store.verify_hash(program_id, parent_hash):
        store.log_audit_event(
            "sync_pull",
            ip_address=client_ip,
            program_id=program_id,
            success=False,
            details={"reason": "hash_mismatch"},
        )
        raise PermissionError("parent_password_hash does not match the stored hash")

    record = store.get_program(program_id)
    if not record:
        store.log_audit_event(
            "sync_pull",
            ip_address=client_ip,
            program_id=program_id,
            success=False,
            details={"reason": "program_not_found"},
        )
        raise LookupError("Program snapshot was not found")

    stored_snapshot = dict(record.get("snapshot") or {})
    store.log_audit_event(
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
