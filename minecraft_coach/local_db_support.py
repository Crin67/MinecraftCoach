from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .app_shared import DEFAULT_BREAK_SECONDS, TASKS_PER_BREAK


SCHEMA_VERSION = 1

DEFAULT_SETTINGS: dict[str, Any] = {
    "window_language": "ru",
    "window_geometry": "1320x840",
    "break_seconds": DEFAULT_BREAK_SECONDS,
    "tasks_per_break": TASKS_PER_BREAK,
    "lesson_seconds": 45,
    "manual_pause_uses": 1,
    "manual_pause_minutes": 2,
    "pause_upgrade_level": 0,
    "shop_extra_pause_tokens": 0,
    "shop_pending_delay_bonus_seconds": 0,
    "lan_admin_enabled": True,
    "lan_admin_port": 8765,
    "pause_minecraft_on_break": True,
    "pause_audio_during_break": False,
    "server_base_url": "",
}

DEFAULT_PARENT_PASSWORD = "1234"
BUILT_IN_CONTENT_STATE_KEY = "built_in_content_version"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def json_to_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def json_from_text(raw: str | None, default: Any) -> Any:
    if raw in (None, ""):
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def safe_title(value: str | None, fallback: str) -> str:
    value = (value or "").strip()
    return value or fallback


def relative_to_or_none(path: Path, base: Path) -> Path | None:
    try:
        return path.relative_to(base)
    except ValueError:
        return None


def task_topic_defaults(task: dict[str, Any]) -> tuple[str, str | None]:
    mode = task.get("mode") or "child"
    if mode == "child":
        grade = int(task.get("grade") or 1)
        return f"topic-child-{grade}", f"level-child-{grade}"
    if mode == "adult":
        theme = (task.get("theme") or "basics").strip().lower()
        if theme == "memory":
            return "topic-memory-core", None
        return f"topic-adult-{theme}", None
    return "topic-memory-core", None


def normalize_task_records(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_tasks: list[dict[str, Any]] = []
    for index, task in enumerate(tasks, start=1):
        normalized = {
            "id": str(task.get("id") or f"task-{index:04d}"),
            "mode": task.get("mode") or ("child" if task.get("grade") else "adult"),
            "grade": task.get("grade"),
            "theme": task.get("theme"),
            "type": task.get("type") or task.get("task_type") or "input",
            "title_ru": safe_title(task.get("title_ru"), "Задание"),
            "title_pl": safe_title(task.get("title_pl"), "Zadanie"),
            "title_en": safe_title(task.get("title_en"), task.get("title_pl") or task.get("title_ru") or "Task"),
            "prompt_ru": safe_title(task.get("prompt_ru"), task.get("title_ru") or "Задание"),
            "prompt_pl": safe_title(task.get("prompt_pl"), task.get("title_pl") or "Zadanie"),
            "prompt_en": safe_title(task.get("prompt_en"), task.get("prompt_pl") or task.get("prompt_ru") or "Task"),
            "answer": task.get("answer", ""),
            "options": list(task.get("options") or []),
            "hint_type": task.get("hint_type") or "math",
            "source": task.get("source") or "built_in",
            "metadata": dict(task.get("metadata") or {}),
            "sort_order": int(task.get("sort_order") or 0),
        }
        if normalized["mode"] == "child" and normalized["grade"] is None:
            normalized["grade"] = 1
        normalized_tasks.append(normalized)
    return normalized_tasks


def normalize_stats_payload(stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "coins": int(stats.get("coins", 0) or 0),
        "correct": int(
            stats.get("correct")
            or stats.get("total_tasks_completed")
            or stats.get("solved_total")
            or 0
        ),
        "wrong": int(
            stats.get("wrong")
            or stats.get("wrong_answers")
            or stats.get("wrong_total")
            or 0
        ),
        "completed_breaks": int(
            stats.get("completed_breaks")
            or stats.get("total_breaks_completed")
            or 0
        ),
        "adult_completed": int(stats.get("adult_completed", 0) or 0),
        "child_completed": int(stats.get("child_completed", 0) or 0),
        "memory_completed": int(stats.get("memory_completed", 0) or 0),
        "last_mode": str(stats.get("last_mode", "") or ""),
        "last_activity": str(stats.get("last_activity", "") or ""),
    }


def answer_display(answer: Any) -> str:
    if isinstance(answer, list):
        return ", ".join(str(item) for item in answer)
    return str(answer or "")


def accepted_answers_from_task(task: dict[str, Any]) -> list[str]:
    task_type = task.get("type") or task.get("task_type")
    answer = task.get("answer")
    if task_type == "reading":
        return ["__read__"]
    if task_type == "memory":
        return ["__memory__"]
    if isinstance(answer, list):
        return [str(item) for item in answer if str(item).strip()]
    if answer in (None, ""):
        return []
    return [str(answer)]


def public_settings_dict(settings: dict[str, Any]) -> dict[str, Any]:
    public_settings = dict(settings)
    public_settings.pop("parent_password_hash", None)
    public_settings.pop("parent_password", None)
    return public_settings
