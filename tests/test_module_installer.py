from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from minecraft_coach.module_installer import (
    ModuleImportError,
    create_module_from_template,
    import_module_source,
    save_module_json,
    validate_module_payload,
)
from tests.support import sample_module_payload


class ModuleInstallerTests(unittest.TestCase):
    def test_validate_module_payload_rejects_missing_topics(self) -> None:
        payload = sample_module_payload()
        payload.pop("topics")

        with self.assertRaises(ModuleImportError):
            validate_module_payload(payload)

    def test_save_module_json_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            module_dir = Path(temp_dir) / "saved-module"
            payload = sample_module_payload(module_id="saved-module", slug="saved-module")

            manifest_path = save_module_json(module_dir, payload)

            self.assertTrue(manifest_path.exists())
            saved = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["id"], "saved-module")

    def test_import_module_source_installs_json_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "module.json"
            modules_dir = root / "modules"
            backups_dir = root / "backups"
            payload = sample_module_payload(module_id="imported", slug="imported")
            source.write_text(json.dumps(payload), encoding="utf-8")

            result = import_module_source(source, modules_dir, backups_dir=backups_dir)

            target_manifest = modules_dir / "imported" / "module.json"
            self.assertEqual(result["module_id"], "imported")
            self.assertTrue(target_manifest.exists())

    def test_create_module_from_template_copies_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template_dir = root / "template"
            template_dir.mkdir()
            (template_dir / "module.json").write_text(
                json.dumps(sample_module_payload(module_id="templated", slug="templated")),
                encoding="utf-8",
            )

            created = create_module_from_template(template_dir, root / "modules", folder_name="new-module")

            self.assertTrue((created / "module.json").exists())
            self.assertEqual(created.name, "new-module")


if __name__ == "__main__":
    unittest.main()
