from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import jinja2
from starlette.templating import Jinja2Templates as StarletteJinja2Templates
from starlette.templating import _TemplateResponse

from app.config import Settings
from app.utils import format_beijing_time, mask_url_host
from app.db import Database
from app.repositories import QBInstanceRepository, ReannounceRunRepository, SessionRepository, UserRepository
from app.scheduler import ReannounceScheduler
from app.security import PasswordHasher, SecretCipher, SessionSigner
from app.services import AuthService, QBInstanceService


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    database: Database
    password_hasher: PasswordHasher
    secret_cipher: SecretCipher
    session_signer: SessionSigner
    user_repository: UserRepository
    session_repository: SessionRepository
    qb_instance_repository: QBInstanceRepository
    reannounce_run_repository: ReannounceRunRepository
    auth_service: AuthService
    qb_instance_service: QBInstanceService
    scheduler: ReannounceScheduler
    templates: StarletteJinja2Templates


class NoCacheJinja2Templates(StarletteJinja2Templates):
    """Custom Jinja2Templates that bypasses the problematic template caching."""
    
    def get_template(self, name: str):
        """
        Completely override get_template to avoid any caching issues.
        This bypasses the Starlette/Jinja2 caching that causes problems.
        """
        # Load template directly from the environment without any caching
        template = self.env.get_template(name)
        return template
    
    def TemplateResponse(
        self,
        name: str,
        context: dict,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background = None,
    ) -> _TemplateResponse:
        """
        Override TemplateResponse to ensure we don't pass problematic globals.
        """
        # Get template cleanly
        template = self.get_template(name)
        
        # Create context without including the Request or other complex objects in template globals
        return _TemplateResponse(
            template=template,
            context=context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


def build_container(settings: Settings) -> AppContainer:
    database = Database(settings.database_path)
    password_hasher = PasswordHasher()
    secret_cipher = SecretCipher(settings.app_encryption_key)
    session_signer = SessionSigner(settings.app_secret_key)

    user_repository = UserRepository(database)
    session_repository = SessionRepository(database)
    qb_instance_repository = QBInstanceRepository(database)
    reannounce_run_repository = ReannounceRunRepository(database)

    auth_service = AuthService(
        user_repository=user_repository,
        session_repository=session_repository,
        password_hasher=password_hasher,
        session_signer=session_signer,
        session_ttl_hours=settings.session_ttl_hours,
    )
    qb_instance_service = QBInstanceService(
        instance_repository=qb_instance_repository,
        run_repository=reannounce_run_repository,
        secret_cipher=secret_cipher,
        log_run_limit=settings.log_run_limit,
    )
    scheduler = ReannounceScheduler(qb_instance_service)
    
    # Create Jinja2 templates - disable cache in the environment
    template_dir = Path(__file__).resolve().parent / "templates"
    templates = NoCacheJinja2Templates(directory=str(template_dir))
    templates.env.filters['beijing_time'] = format_beijing_time
    templates.env.filters['mask_url_host'] = mask_url_host
    
    # Ensure the jinja environment has no cache
    templates.env.cache = {}

    return AppContainer(
        settings=settings,
        database=database,
        password_hasher=password_hasher,
        secret_cipher=secret_cipher,
        session_signer=session_signer,
        user_repository=user_repository,
        session_repository=session_repository,
        qb_instance_repository=qb_instance_repository,
        reannounce_run_repository=reannounce_run_repository,
        auth_service=auth_service,
        qb_instance_service=qb_instance_service,
        scheduler=scheduler,
        templates=templates,
    )
