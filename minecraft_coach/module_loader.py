from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

MODULE_MANIFEST_NAMES = ("module.json", "module.py")


def load_modules(modules_dir: Path) -> list[dict[str, Any]]:
    modules: list[dict[str, Any]] = []
    base_dir = Path(modules_dir)
    if not base_dir.exists():
        return modules

    for folder in sorted(path for path in base_dir.iterdir() if path.is_dir()):
        manifest_path = find_module_manifest(folder)
        if not manifest_path:
            continue
        try:
            payload = load_module_payload(manifest_path)
        except Exception:
            # A broken drop-in module should not stop the whole app from starting.
            continue
        if not payload:
            continue
        payload = dict(payload)
        payload.setdefault("id", folder.name)
        payload.setdefault("slug", folder.name.replace("_", "-"))
        payload.setdefault("sort_order", 100)
        payload["manifest_path"] = str(manifest_path)
        modules.append(payload)

    modules.sort(key=lambda item: (int(item.get("sort_order", 1000)), str(item.get("title_ru") or item.get("slug") or "")))
    return modules


def find_module_manifest(path: Path) -> Path | None:
    candidate = Path(path)
    if candidate.is_file() and candidate.name in MODULE_MANIFEST_NAMES:
        return candidate
    if not candidate.is_dir():
        return None

    for name in MODULE_MANIFEST_NAMES:
        direct = candidate / name
        if direct.exists():
            return direct

    manifests = sorted(
        (
            manifest
            for name in MODULE_MANIFEST_NAMES
            for manifest in candidate.rglob(name)
        ),
        key=lambda item: (len(item.relative_to(candidate).parts), str(item)),
    )
    return manifests[0] if manifests else None


def load_module_payload(module_path: Path) -> dict[str, Any] | None:
    if module_path.suffix.lower() == ".json":
        return _load_json_payload(module_path)

    module_name = f"minecraft_coach_dynamic_{module_path.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "build_module"):
        payload = module.build_module()
    else:
        payload = getattr(module, "MODULE", None)
    if not isinstance(payload, dict):
        return None
    return payload


def _load_json_payload(module_path: Path) -> dict[str, Any] | None:
    payload = json.loads(module_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None
    return payload
