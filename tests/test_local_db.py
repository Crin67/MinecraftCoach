from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from minecraft_coach.local_db import LocalDB


class LocalDBTests(unittest.TestCase):
    def create_db(self) -> LocalDB:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return LocalDB(
            root / "coach_data" / "coach.db",
            data_dir=root / "coach_data",
            assets_dir=root / "assets",
            modules_dir=root / "modules",
        )

    def test_temp_database_bootstraps_snapshots(self) -> None:
        db = self.create_db()

        settings = db.get_settings()
        dashboard = db.get_dashboard_snapshot()
        content = db.get_content_snapshot()

        self.assertIn("program_id", settings)
        self.assertGreater(dashboard["counts"]["topics"], 0)
        self.assertGreater(dashboard["counts"]["tasks"], 0)
        self.assertTrue(content["topics"])
        self.assertTrue(content["tasks"])

    def test_update_settings_and_parent_password(self) -> None:
        db = self.create_db()

        updated = db.update_settings(
            {
                "window_language": "en",
                "break_seconds": 600,
                "server_base_url": "http://localhost:8000",
            }
        )
        db.update_parent_password("new-password")

        self.assertEqual(updated["window_language"], "en")
        self.assertEqual(updated["break_seconds"], 600)
        self.assertEqual(updated["server_base_url"], "http://localhost:8000")
        self.assertTrue(db.verify_parent_password("new-password"))
        self.assertFalse(db.verify_parent_password("wrong-password"))


if __name__ == "__main__":
    unittest.main()
