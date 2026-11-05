"""Database engine + session. Works with PostgreSQL (prod) and SQLite (local dev / tests)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


def _fix_url(url: str) -> str:
    # Supabase/Render give "postgres://..." or "postgresql://..."; we use the psycopg v3 driver.
    for old in ("postgres://", "postgresql://"):
        if url.startswith(old):
            return "postgresql+psycopg://" + url[len(old):]
    return url


_url = _fix_url(settings.DATABASE_URL)
engine = create_engine(
    _url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if _url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """FastAPI dependency: one DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if missing. MVP shortcut; move to Alembic migrations before launch."""
    from . import models  # noqa: F401  (registers tables on Base)
    Base.metadata.create_all(engine)
