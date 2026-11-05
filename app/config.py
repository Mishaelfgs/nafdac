"""Central settings. Every secret comes from an environment variable (see .env.example)."""
import os


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


class Settings:
    def __init__(self) -> None:
        self.ENV = _get("ENV", "dev")
        self.DATABASE_URL = _get("DATABASE_URL", "sqlite:///./dev.db")
        self.WHATSAPP_DRY_RUN = _get("WHATSAPP_DRY_RUN", "true").lower() == "true"
        self.WHATSAPP_TOKEN = _get("WHATSAPP_TOKEN")
        self.WHATSAPP_PHONE_NUMBER_ID = _get("WHATSAPP_PHONE_NUMBER_ID")
        self.WHATSAPP_VERIFY_TOKEN = _get("WHATSAPP_VERIFY_TOKEN")
        self.WHATSAPP_APP_SECRET = _get("WHATSAPP_APP_SECRET")
        self.WHATSAPP_API_VERSION = _get("WHATSAPP_API_VERSION", "v21.0")
        # Dev-only defaults so the app runs locally. Production refuses to start with them.
        self.PHONE_HASH_SALT = _get("PHONE_HASH_SALT", "dev-salt-change-me")
        self.SESSION_SECRET = _get("SESSION_SECRET", "dev-session-secret-change-me")
        self.RATE_LIMIT_PER_HOUR = int(_get("RATE_LIMIT_PER_HOUR", "20"))

    @property
    def is_prod(self) -> bool:
        return self.ENV == "prod"

    def validate_for_production(self) -> None:
        """Called at startup. Stops the app if it is mis-configured in prod."""
        if not self.is_prod:
            return
        missing = [
            n for n in ("WHATSAPP_VERIFY_TOKEN", "WHATSAPP_APP_SECRET", "PHONE_HASH_SALT", "SESSION_SECRET")
            if not _get(n)
        ]
        if missing:
            raise RuntimeError(f"Missing required env vars for prod: {', '.join(missing)}")


settings = Settings()
