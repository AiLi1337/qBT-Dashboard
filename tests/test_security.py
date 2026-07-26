from __future__ import annotations

from app.security import PasswordHasher, SecretCipher, SessionSigner


def test_password_hash_round_trip():
    hasher = PasswordHasher()
    password_hash = hasher.hash_password("secret")
    assert hasher.verify_password("secret", password_hash)
    assert not hasher.verify_password("wrong", password_hash)


def test_secret_cipher_round_trip():
    from cryptography.fernet import Fernet

    cipher = SecretCipher(Fernet.generate_key().decode())
    encrypted = cipher.encrypt("qb-password")
    assert encrypted != "qb-password"
    assert cipher.decrypt(encrypted) == "qb-password"


def test_session_signer_validates_signature():
    signer = SessionSigner("session-secret")
    signed = signer.sign("abc123")
    assert signer.unsign(signed) == "abc123"
    assert signer.unsign(signed + "tampered") is None

def test_assert_public_url_allows_private_instance_urls():
    from app.utils import assert_public_url
    import pytest

    # instance base_url is admin-trusted: private/loopback IP literals OK
    assert_public_url("http://127.0.0.1:8080", allow_private=True)
    assert_public_url("http://localhost:8080", allow_private=True)
    # plain hostnames pass without DNS resolution (offline-safe)
    assert assert_public_url("http://qb.local") is not None
    # user-supplied torrent URLs stay strict: private IP literal blocked
    with pytest.raises(ValueError):
        assert_public_url("http://127.0.0.1/x.torrent")
    with pytest.raises(ValueError):
        assert_public_url("http://localhost/x.torrent")
    # bad scheme rejected
    with pytest.raises(ValueError):
        assert_public_url("ftp://example.com/x")
