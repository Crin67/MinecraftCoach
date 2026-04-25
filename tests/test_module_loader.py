from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from minecraft_coach.module_loader import (
    find_module_manifest,
    load_module_payload,
    load_modules,
)
from tests.support import sample_module_payload


class ModuleLoaderTests(unittest.TestCase):
    def test_find_module_manifest_prefers_direct_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            module_root = Path(temp_dir) / "sample"
            module_root.mkdir()
            manifest_path = module_root / "module.json"
            manifest_path.write_text(json.dumps(sample_module_payload()), encoding="utf-8")

            self.assertEqual(find_module_manifest(module_root), manifest_path)

    def test_load_module_payload_supports_python_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            module_root = Path(temp_dir) / "sample_py"
            module_root.mkdir()
            manifest_path = module_root / "module.py"
            manifest_path.write_text(
                "MODULE = "
                + repr(sample_module_payload(module_id="python-module", slug="python-module")),
                encoding="utf-8",
            )

            payload = load_module_payload(manifest_path)

            self.assertIsNotNone(payload)
            self.assertEqual(payload["id"], "python-module")

    def test_load_modules_returns_sorted_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            modules_dir = Path(temp_dir)

            later = modules_dir / "later"
            later.mkdir()
            later_payload = sample_module_payload(module_id="later", slug="later")
            later_payload["sort_order"] = 20
            (later / "module.json").write_text(json.dumps(later_payload), encoding="utf-8")

            earlier = modules_dir / "earlier"
            earlier.mkdir()
            earlier_payload = sample_module_payload(module_id="earlier", slug="earlier")
            earlier_payload["sort_order"] = 5
            (earlier / "module.json").write_text(json.dumps(earlier_payload), encoding="utf-8")

            loaded = load_modules(modules_dir)

            self.assertEqual([item["id"] for item in loaded], ["earlier", "later"])
            self.assertTrue(all("manifest_path" in item for item in loaded))


if __name__ == "__main__":
    unittest.main()
