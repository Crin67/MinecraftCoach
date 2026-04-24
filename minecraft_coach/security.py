from __future__ import annotations

import base64
import hashlib
import hmac
import os


SCRYPT_PREFIX = "scrypt"
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 64


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))


def is_password_hash(value: str | None) -> bool:
    return bool(value and value.startswith(f"{SCRYPT_PREFIX}$"))


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    salt = salt or os.urandom(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return (
        f"{SCRYPT_PREFIX}${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${SCRYPT_DKLEN}$"
        f"{_b64encode(salt)}${_b64encode(digest)}"
    )


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not password or not stored_hash:
        return False
    if not is_password_hash(stored_hash):
        return hmac.compare_digest(password, stored_hash)
    try:
        prefix, n, r, p, dklen, salt_b64, digest_b64 = stored_hash.split("$", 6)
        if prefix != SCRYPT_PREFIX:
            return False
        salt = _b64decode(salt_b64)
        expected = _b64decode(digest_b64)
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=int(dklen),
        )
    except Exception:
        return False
    return hmac.compare_digest(actual, expected)
