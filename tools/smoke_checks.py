from __future__ import annotations

import sys
import tempfile
import warnings
from pathlib import Path
import shutil

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

warnings.filterwarnings("ignore", category=ResourceWarning)

from minecraft_coach.local_db import LocalDB
from minecraft_coach.module_loader import load_modules
from minecraft_coach.security import hash_password
from server.app import main as server_main


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def smoke_local_db() -> None:
    root = Path(tempfile.mkdtemp())
    try:
        db = LocalDB(
            root / "coach_data" / "coach.db",
            data_dir=root / "coach_data",
            assets_dir=root / "assets",
            modules_dir=root / "modules",
        )
        snapshot = db.get_dashboard_snapshot()
        assert_true(snapshot["counts"]["topics"] > 0, "LocalDB should bootstrap topics")
        assert_true(snapshot["counts"]["tasks"] > 0, "LocalDB should bootstrap tasks")
        db.update_parent_password("smoke-pass")
        assert_true(db.verify_parent_password("smoke-pass"), "LocalDB password update should verify")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def smoke_backend_helpers() -> None:
    payload = server_main.SyncEnvelope(
        program_id="AB12",
        device_id="desktop-v23",
        checkpoint="smoke-check",
        parent_password_hash=hash_password("1234", salt=b"0123456789abcdef"),
        payload={"dashboard": {}, "runtime": {}, "content": {}},
    )
    canonical = server_main.canonical_sync_envelope(payload)
    assert_true(canonical["program_id"] == "AB12", "Program id should remain normalized")
    assert_true(server_main.health()["status"] == "ok", "Health endpoint should report ok")
    assert_true(server_main.downloads_catalog()["ok"], "Downloads catalog should report ok")


def smoke_modules() -> None:
    modules = load_modules(Path("modules"))
    assert_true(len(modules) >= 2, "Expected bundled modules to load")
    assert_true(all(item.get("manifest_path") for item in modules), "Loaded modules should expose manifest_path")


def smoke_routes() -> None:
    route_paths = {getattr(route, "path", "") for route in server_main.app.routes}
    required = {
        "/health",
        "/downloads/catalog",
        "/auth/login",
        "/dashboard",
        "/content",
        "/sync/push",
        "/sync/pull",
    }
    missing = sorted(required - route_paths)
    assert_true(not missing, f"Missing expected routes: {', '.join(missing)}")


def main() -> None:
    smoke_local_db()
    smoke_backend_helpers()
    smoke_modules()
    smoke_routes()
    print("Smoke checks passed.")


if __name__ == "__main__":
    main()
