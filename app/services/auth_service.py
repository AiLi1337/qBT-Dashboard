from __future__ import annotations

import hmac
from datetime import datetime
from typing import Optional

from app.domain import Session, SessionContext, User
from app.repositories import SessionRepository, UserRepository
from app.security import PasswordHasher, SessionSigner, generate_csrf_token, generate_session_id
from app.utils import add_hours_iso, utc_now, utc_now_iso


class AuthError(RuntimeError):
    pass


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        password_hasher: PasswordHasher,
        session_signer: SessionSigner,
        session_ttl_hours: int,
    ) -> None:
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.password_hasher = password_hasher
        self.session_signer = session_signer
        self.session_ttl_hours = session_ttl_hours

    def ensure_bootstrap_admin(self, username: str, password: str) -> User:
        existing = self.user_repository.get_by_username(username)
        if existing is not None:
            return existing
        if self.user_repository.count() > 0:
            raise AuthError("Administrator already initialized with a different username")
        password_hash = self.password_hasher.hash_password(password)
        return self.user_repository.create(username, password_hash)

    def login(self, username: str, password: str) -> tuple[SessionContext, str]:
        self.session_repository.delete_expired()
        user = self.user_repository.get_by_username(username)
        if user is None or not self.password_hasher.verify_password(password, user.password_hash):
            raise AuthError("账号或密码错误")

        session = Session(
            session_id=generate_session_id(),
            user_id=user.id,
            csrf_token=generate_csrf_token(),
            created_at=utc_now_iso(),
            expires_at=add_hours_iso(self.session_ttl_hours),
        )
        self.session_repository.create(session)
        signed_session = self.session_signer.sign(session.session_id)
        return SessionContext(user=user, session=session), signed_session

    def logout(self, signed_session_id: Optional[str]) -> None:
        session_id = self.session_signer.unsign(signed_session_id)
        if session_id:
            self.session_repository.delete(session_id)

    def authenticate(self, signed_session_id: Optional[str]) -> SessionContext:
        self.session_repository.delete_expired()
        session_id = self.session_signer.unsign(signed_session_id)
        if not session_id:
            raise AuthError("未登录")
        session = self.session_repository.get(session_id)
        if session is None:
            raise AuthError("会话已失效")
        if datetime.fromisoformat(session.expires_at) <= utc_now():
            self.session_repository.delete(session.session_id)
            raise AuthError("会话已过期")
        user = self.user_repository.get_by_id(session.user_id)
        if user is None:
            self.session_repository.delete(session.session_id)
            raise AuthError("用户不存在")
        return SessionContext(user=user, session=session)

    def verify_csrf(self, session_context: SessionContext, csrf_header: Optional[str], csrf_cookie: Optional[str]) -> None:
        expected = session_context.session.csrf_token
        if not csrf_header or not csrf_cookie or not hmac.compare_digest(csrf_header, expected) or not hmac.compare_digest(csrf_cookie, expected):
            raise AuthError("CSRF 校验失败")
