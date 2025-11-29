# core/security.py
from fastapi import Header
from core.errors import Unauthorized, ServerMisconfigured
from core.settings import Settings


def build_admin_required(settings: Settings):
    """
    Build an admin dependency bound to a specific Settings instance.
    This avoids any global settings and makes the dependency test-safe.
    """

    def admin_required(x_admin_key: str = Header(None)):
        if settings.admin_api_key is None:
            # Misconfigured server — not a client error
            raise ServerMisconfigured("ADMIN_API_KEY not configured")

        if x_admin_key != settings.admin_api_key:
            raise Unauthorized("Invalid or missing admin key")

    return admin_required
