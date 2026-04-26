from __future__ import annotations

import unittest
from datetime import datetime, timezone

from server.app.storage import (
    build_audit_event_payload,
    build_public_program_record,
    normalize_snapshot_input,
    rate_limit_headers,
)
from minecraft_coach.security import hash_password


class StorageHelperTests(unittest.TestCase):
    def test_normalize_snapshot_input_normalizes_contract_fields(self) -> None:
        normalized = normalize_snapshot_input(
            program_id="ab12",
            parent_password_hash=hash_password("1234", salt=b"fedcba9876543210"),
            payload={"runtime": {"state": "menu"}},
            device_id="desktop-v23",
            checkpoint="cp-1",
        )

        self.assertEqual(normalized["program_id"], "AB12")
        self.assertEqual(normalized["device_id"], "desktop-v23")
        self.assertEqual(normalized["checkpoint"], "cp-1")
        self.assertEqual(normalized["payload"], {"runtime": {"state": "menu"}})

    def test_build_public_program_record_formats_datetime(self) -> None:
        updated_at = datetime(2026, 4, 26, 12, 30, 15, 123456, tzinfo=timezone.utc)
        payload = build_public_program_record(
            program_id="AB12",
            device_id="desktop-v23",
            checkpoint="cp-1",
            updated_at=updated_at,
            snapshot={"content": {"topics": 3}},
        )

        self.assertEqual(payload["updated_at"], "2026-04-26T12:30:15+00:00")
        self.assertEqual(payload["snapshot"], {"content": {"topics": 3}})

    def test_rate_limit_headers_keep_expected_shape(self) -> None:
        self.assertEqual(
            rate_limit_headers(60, 12),
            {
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Remaining": "12",
            },
        )

    def test_build_audit_event_payload_keeps_default_details(self) -> None:
        payload = build_audit_event_payload("sync_push", created_at="2026-04-26T12:30:15+00:00")

        self.assertEqual(payload["event_type"], "sync_push")
        self.assertEqual(payload["details"], {})
        self.assertTrue(payload["success"])


if __name__ == "__main__":
    unittest.main()
