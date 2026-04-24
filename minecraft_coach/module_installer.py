from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from .module_loader import find_module_manifest, load_module_payload

IGNORED_COPY_NAMES = ("__pycache__", ".git", ".DS_Store", "Thumbs.db")


class ModuleImportError(ValueError):
    pass


def list_installed_modules(modules_dir: Path) -> list[dict[str, object]]:
    modules_dir = Path(modules_dir)
    installed: list[dict[str, object]] = []
    if not modules_dir.exists():
        return installed
    for folder in sorted(path for path in modules_dir.iterdir() if path.is_dir()):
        manifest = find_module_manifest(folder)
        if not manifest:
            continue
        row: dict[str, object] = {
            "folder": folder,
            "manifest_path": manifest,
            "manifest_type": manifest.suffix.lower().lstrip("."),
            "id": folder.name,
            "slug": folder.name,
            "title_ru": folder.name,
            "title_pl": folder.name,
            "title_en": folder.name,
            "payload": None,
            "error": "",
            "raw_text": "",
        }
        try:
            payload = load_module_payload(manifest) or {}
            row["payload"] = payload
            row["id"] = str(payload.get("id") or folder.name)
            row["slug"] = str(payload.get("slug") or row["id"])
            row["title_ru"] = str(payload.get("title_ru") or payload.get("slug") or row["id"])
            row["title_pl"] = str(payload.get("title_pl") or row["title_ru"])
            row["title_en"] = str(payload.get("title_en") or row["title_ru"])
        except Exception as exc:
            row["error"] = str(exc)
            if manifest.suffix.lower() == ".json":
                try:
                    row["raw_text"] = manifest.read_text(encoding="utf-8")
                except Exception:
                    row["raw_text"] = ""
        installed.append(row)
    return installed


def import_module_source(
    source: Path,
    modules_dir: Path,
    *,
    backups_dir: Path | None = None,
) -> dict[str, str]:
    source = Path(source)
    modules_dir = Path(modules_dir)
    backups_dir = Path(backups_dir) if backups_dir else modules_dir.parent / "module_backups"
    modules_dir.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        return _install_from_folder(source, source.name, modules_dir, backups_dir)
    if not source.exists():
        raise ModuleImportError(f"Module source was not found: {source}")
    if source.suffix.lower() == ".zip":
        with tempfile.TemporaryDirectory(prefix="coach_module_") as temp_dir:
            temp_root = Path(temp_dir)
            with zipfile.ZipFile(source) as archive:
                archive.extractall(temp_root)
            return _install_from_folder(temp_root, source.stem, modules_dir, backups_dir)
    if source.suffix.lower() in {".json", ".py"}:
        payload = load_module_payload(source)
        if not payload:
            raise ModuleImportError("The selected file does not contain a valid module payload.")
        return _install_manifest_file(source, payload, modules_dir, backups_dir)
    raise ModuleImportError("Supported import formats are folder, .zip, .json, or .py.")


def export_module_template(template_dir: Path, destination_root: Path) -> Path:
    template_dir = Path(template_dir)
    destination_root = Path(destination_root)
    if not template_dir.exists():
        raise ModuleImportError(f"Template folder was not found: {template_dir}")
    destination_root.mkdir(parents=True, exist_ok=True)
    target_dir = _unique_path(destination_root / template_dir.name)
    shutil.copytree(template_dir, target_dir, ignore=shutil.ignore_patterns(*IGNORED_COPY_NAMES))
    return target_dir


def create_module_from_template(
    template_dir: Path,
    modules_dir: Path,
    *,
    folder_name: str | None = None,
) -> Path:
    template_dir = Path(template_dir)
    modules_dir = Path(modules_dir)
    if not template_dir.exists():
        raise ModuleImportError(f"Template folder was not found: {template_dir}")
    modules_dir.mkdir(parents=True, exist_ok=True)
    base_name = _sanitize_name(folder_name or f"new-module-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    target_dir = _unique_path(modules_dir / base_name)
    shutil.copytree(template_dir, target_dir, ignore=shutil.ignore_patterns(*IGNORED_COPY_NAMES))
    return target_dir


def save_module_json(module_dir: Path, payload: dict) -> Path:
    module_dir = Path(module_dir)
    validate_module_payload(payload)
    module_dir.mkdir(parents=True, exist_ok=True)
    target = module_dir / "module.json"
    temp = module_dir / "module.json.tmp"
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(target)
    return target


def validate_module_payload(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise ModuleImportError("Module JSON must contain an object at the top level.")

    required_top = [
        "id",
        "slug",
        "title_ru",
        "title_pl",
        "title_en",
        "description_ru",
        "description_pl",
        "description_en",
        "topics",
    ]
    missing = [key for key in required_top if key not in payload]
    if missing:
        raise ModuleImportError(f"Module JSON is missing required fields: {', '.join(missing)}")

    if not isinstance(payload.get("topics"), list):
        raise ModuleImportError("Field 'topics' must be a list.")
    if payload.get("levels") is not None and not isinstance(payload.get("levels"), list):
        raise ModuleImportError("Field 'levels' must be a list when present.")

    topic_ids: set[str] = set()
    task_ids: set[str] = set()
    for topic_index, topic in enumerate(payload.get("topics") or [], start=1):
        if not isinstance(topic, dict):
            raise ModuleImportError(f"Topic #{topic_index} must be an object.")
        topic_required = [
            "id",
            "slug",
            "mode",
            "title_ru",
            "title_pl",
            "title_en",
            "description_ru",
            "description_pl",
            "description_en",
            "lessons",
            "tasks",
        ]
        missing_topic = [key for key in topic_required if key not in topic]
        if missing_topic:
            raise ModuleImportError(f"Topic #{topic_index} is missing fields: {', '.join(missing_topic)}")

        topic_id = str(topic.get("id") or "").strip()
        if not topic_id:
            raise ModuleImportError(f"Topic #{topic_index} has an empty id.")
        if topic_id in topic_ids:
            raise ModuleImportError(f"Duplicate topic id found: {topic_id}")
        topic_ids.add(topic_id)

        if not isinstance(topic.get("lessons"), list):
            raise ModuleImportError(f"Topic '{topic_id}' field 'lessons' must be a list.")
        if not isinstance(topic.get("tasks"), list):
            raise ModuleImportError(f"Topic '{topic_id}' field 'tasks' must be a list.")

        for lesson_index, lesson in enumerate(topic.get("lessons") or [], start=1):
            if not isinstance(lesson, dict):
                raise ModuleImportError(f"Lesson #{lesson_index} in topic '{topic_id}' must be an object.")
            for key in ("title_ru", "title_pl", "title_en", "content_ru", "content_pl", "content_en"):
                if key not in lesson:
                    raise ModuleImportError(f"Lesson #{lesson_index} in topic '{topic_id}' is missing field: {key}")

        for task_index, task in enumerate(topic.get("tasks") or [], start=1):
            if not isinstance(task, dict):
                raise ModuleImportError(f"Task #{task_index} in topic '{topic_id}' must be an object.")
            task_required = [
                "id",
                "type",
                "mode",
                "title_ru",
                "title_pl",
                "prompt_ru",
                "prompt_pl",
                "answer",
            ]
            missing_task = [key for key in task_required if key not in task]
            if missing_task:
                raise ModuleImportError(
                    f"Task #{task_index} in topic '{topic_id}' is missing fields: {', '.join(missing_task)}"
                )
            task_id = str(task.get("id") or "").strip()
            if not task_id:
                raise ModuleImportError(f"Task #{task_index} in topic '{topic_id}' has an empty id.")
            if task_id in task_ids:
                raise ModuleImportError(f"Duplicate task id found: {task_id}")
            task_ids.add(task_id)


def _install_from_folder(
    folder: Path,
    fallback_name: str,
    modules_dir: Path,
    backups_dir: Path,
) -> dict[str, str]:
    manifest_path = find_module_manifest(folder)
    if not manifest_path:
        raise ModuleImportError("No module.json or module.py was found in the selected folder.")
    payload = load_module_payload(manifest_path)
    if not payload:
        raise ModuleImportError("The selected folder contains an invalid module manifest.")
    module_root = manifest_path.parent
    module_id, module_slug = _module_identity(payload)
    with tempfile.TemporaryDirectory(prefix="coach_module_stage_") as temp_dir:
        staged_root = Path(temp_dir) / module_root.name
        shutil.copytree(module_root, staged_root, ignore=shutil.ignore_patterns(*IGNORED_COPY_NAMES))
        target_dir, backup_path = _prepare_target_dir(
            modules_dir,
            backups_dir,
            payload,
            fallback_name=fallback_name,
        )
        shutil.copytree(staged_root, target_dir, ignore=shutil.ignore_patterns(*IGNORED_COPY_NAMES))
    return {
        "module_id": module_id,
        "module_slug": module_slug,
        "target_dir": str(target_dir),
        "backup_path": str(backup_path) if backup_path else "",
    }


def _install_manifest_file(
    source: Path,
    payload: dict,
    modules_dir: Path,
    backups_dir: Path,
) -> dict[str, str]:
    module_id, module_slug = _module_identity(payload)
    target_dir, backup_path = _prepare_target_dir(
        modules_dir,
        backups_dir,
        payload,
        fallback_name=source.stem,
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    target_name = "module.json" if source.suffix.lower() == ".json" else "module.py"
    shutil.copy2(source, target_dir / target_name)
    return {
        "module_id": module_id,
        "module_slug": module_slug,
        "target_dir": str(target_dir),
        "backup_path": str(backup_path) if backup_path else "",
    }


def _prepare_target_dir(
    modules_dir: Path,
    backups_dir: Path,
    payload: dict,
    *,
    fallback_name: str,
) -> tuple[Path, Path | None]:
    module_id, module_slug = _module_identity(payload)
    preferred_name = _sanitize_name(module_slug or module_id or fallback_name)
    installed = _installed_module_folders(modules_dir)

    existing_dir: Path | None = None
    for item in installed:
        if item["id"] == module_id or item["slug"] == module_slug:
            existing_dir = item["folder"]
            break

    if existing_dir and existing_dir.exists():
        backups_dir.mkdir(parents=True, exist_ok=True)
        backup_name = f"{existing_dir.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = _unique_path(backups_dir / backup_name)
        shutil.move(str(existing_dir), str(backup_path))
        return existing_dir, backup_path

    target_dir = _unique_path(modules_dir / preferred_name)
    return target_dir, None


def _installed_module_folders(modules_dir: Path) -> list[dict[str, Path | str]]:
    installed: list[dict[str, Path | str]] = []
    for row in list_installed_modules(modules_dir):
        if row.get("error"):
            continue
        installed.append(
            {
                "folder": row["folder"],
                "id": str(row["id"]),
                "slug": str(row["slug"]),
            }
        )
    return installed


def _module_identity(payload: dict) -> tuple[str, str]:
    module_id = str(payload.get("id") or "").strip()
    module_slug = str(payload.get("slug") or module_id).strip()
    if not module_id or not module_slug:
        raise ModuleImportError("The module must define both id and slug.")
    return module_id, module_slug


def _sanitize_name(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value).strip())
    while "--" in safe:
        safe = safe.replace("--", "-")
    safe = safe.strip("-")
    return safe or "module"


def _unique_path(base: Path) -> Path:
    candidate = Path(base)
    suffix = 2
    while candidate.exists():
        candidate = base.parent / f"{base.name}_{suffix}"
        suffix += 1
    return candidate
