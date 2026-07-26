from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Optional

try:
    import bcrypt  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    bcrypt = None
from cryptography.fernet import Fernet, InvalidToken

import logging


class PasswordHasher:
    def hash_password(self, password: str) -> str:
        if bcrypt is not None:
            encoded = password.encode("utf-8")
            return "bcrypt$" + bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
        return "scrypt$" + base64.urlsafe_b64encode(salt).decode("utf-8") + "$" + base64.urlsafe_b64encode(digest).decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        if password_hash.startswith("scrypt$"):
            return self._verify_scrypt(password, password_hash)
        if password_hash.startswith("bcrypt$"):
            return self._verify_bcrypt(password, password_hash.removeprefix("bcrypt$"))
        return self._verify_bcrypt(password, password_hash)

    @staticmethod
    def _verify_bcrypt(password: str, password_hash: str) -> bool:
        if bcrypt is None:
            import logging
            logging.getLogger(__name__).warning("bcrypt not available, cannot verify bcrypt passwords")
            return False
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @staticmethod
    def _verify_scrypt(password: str, password_hash: str) -> bool:
        try:
            _, salt_raw, digest_raw = password_hash.split("$", 2)
            salt = base64.urlsafe_b64decode(salt_raw.encode("utf-8"))
            expected = base64.urlsafe_b64decode(digest_raw.encode("utf-8"))
        except ValueError:
            return False
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)


class SecretCipher:
    def __init__(self, encryption_key: str) -> None:
        self._fernet = Fernet(encryption_key.encode("utf-8"))

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken as e:
            logging.getLogger(__name__).error("Failed to decrypt ciphertext: %s", e)
            raise ValueError("Invalid or corrupted ciphertext") from e


class SessionSigner:
    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key.encode("utf-8")

    def sign(self, session_id: str) -> str:
        digest = hmac.new(self.secret_key, session_id.encode("utf-8"), hashlib.sha256).digest()
        signature = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
        return f"{session_id}.{signature}"

    def unsign(self, signed_value: Optional[str]) -> Optional[str]:
        if not signed_value or "." not in signed_value:
            return None
        session_id, signature = signed_value.rsplit(".", 1)
        expected = self.sign(session_id).rsplit(".", 1)[1]
        if not hmac.compare_digest(signature, expected):
            return None
        return session_id


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)
