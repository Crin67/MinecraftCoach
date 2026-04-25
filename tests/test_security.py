from __future__ import annotations

import unittest

from minecraft_coach.security import hash_password, is_password_hash, verify_password


class SecurityTests(unittest.TestCase):
    def test_hash_password_roundtrip(self) -> None:
        hashed = hash_password("secret-pass", salt=b"0123456789abcdef")

        self.assertTrue(is_password_hash(hashed))
        self.assertTrue(verify_password("secret-pass", hashed))
        self.assertFalse(verify_password("wrong-pass", hashed))

    def test_verify_password_accepts_plaintext_fallback(self) -> None:
        self.assertTrue(verify_password("1234", "1234"))
        self.assertFalse(verify_password("0000", "1234"))


if __name__ == "__main__":
    unittest.main()
