from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import HTTPException

from minecraft_coach.security import hash_password
from server.app import main as server_main


class ServerHelperTests(unittest.TestCase):
    def test_normalize_sync_payload_rejects_unexpected_keys(self) -> None:
        with self.assertRaises(HTTPException) as context:
            server_main.normalize_sync_payload({"invalid": {}})

        self.assertEqual(context.exception.status_code, 400)

    def test_canonical_sync_envelope_normalizes_fields(self) -> None:
        payload = server_main.SyncEnvelope(
            program_id="ab12",
            device_id="desktop-v23",
            checkpoint="checkpoint-1",
            parent_password_hash=hash_password("1234", salt=b"fedcba9876543210"),
            payload={"dashboard": {}, "runtime": {}, "content": {}},
        )

        canonical = server_main.canonical_sync_envelope(payload)

        self.assertEqual(canonical["program_id"], "AB12")
        self.assertEqual(canonical["device_id"], "desktop-v23")
        self.assertIn("payload", canonical)
        self.assertEqual(
            server_main.sync_fingerprint(payload),
            server_main.sync_fingerprint_from_canonical(canonical),
        )

    def test_require_program_id_from_token_uses_store(self) -> None:
        with patch.object(server_main.STORE, "resolve_session", return_value="AB12"):
            self.assertEqual(server_main.require_program_id_from_token("Bearer token"), "AB12")

    def test_downloads_catalog_shape(self) -> None:
        payload = server_main.downloads_catalog()

        self.assertTrue(payload["ok"])
        self.assertIn("app", payload)
        self.assertIn("modules", payload)
        self.assertIsInstance(payload["modules"], list)

    def test_health_reports_ok(self) -> None:
        payload = server_main.health()

        self.assertEqual(payload["status"], "ok")
        self.assertIn("storage", payload)


if __name__ == "__main__":
    unittest.main()
