"""Database tables. All timestamps are UTC (naive datetimes)."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

CATEGORIES = ("drug", "food", "cosmetic", "water", "herbal")
PRODUCT_STATUSES = ("active", "recalled", "suspended")
REPORT_STATUSES = ("pending", "reviewed", "confirmed_fake")
BUSINESS_TYPES = ("pharmacy", "manufacturer", "distributor")


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _in(col: str, values: tuple) -> str:
    return f"{col} IN ({', '.join(repr(v) for v in values)})"


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(_in("category", CATEGORIES), name="ck_products_category"),
        CheckConstraint(_in("status", PRODUCT_STATUSES), name="ck_products_status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(255), index=True)
    nafdac_number: Mapped[str] = mapped_column(String(32))            # as displayed, e.g. "A4-1001"
    nafdac_key: Mapped[str] = mapped_column(String(32), unique=True)  # normalised lookup key, e.g. "A41001"
    manufacturer: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(20))
    pack_sizes: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="active")
    expiry_info: Mapped[str | None] = mapped_column(String(255))      # free text, e.g. registration validity
    barcode: Mapped[str | None] = mapped_column(String(64))           # OPTIONAL: many real products have none
    photo_url: Mapped[str | None] = mapped_column(String(500))
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)   # True = fake demo row, NOT real data
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class RecalledBatch(Base):
    """A specific batch of a registered product that has been recalled."""
    __tablename__ = "recalled_batches"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    batch_no: Mapped[str] = mapped_column(String(64))                 # stored UPPERCASE
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Check(Base):
    __tablename__ = "checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_hash: Mapped[str] = mapped_column(String(64), index=True)   # never the raw phone number
    input_type: Mapped[str] = mapped_column(String(30))
    input_text: Mapped[str | None] = mapped_column(String(200))
    verdict: Mapped[str] = mapped_column(String(20), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    language: Mapped[str] = mapped_column(String(5))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Report(Base):
    """Fake-product reports (flow built in Phase 2). No phone number stored."""
    __tablename__ = "reports"
    __table_args__ = (CheckConstraint(_in("status", REPORT_STATUSES), name="ck_reports_status"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    photo_url: Mapped[str | None] = mapped_column(String(500))
    location_text: Mapped[str | None] = mapped_column(String(255))    # coarse only (area/city), never GPS
    market_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (CheckConstraint(_in("type", BUSINESS_TYPES), name="ck_businesses_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    business_name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(20))
    subscription_status: Mapped[str] = mapped_column(String(20), default="none")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AdminUser(Base):
    __tablename__ = "users_admin"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="admin")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class WaSession(Base):
    """Where each WhatsApp user is in the chat (language + current step)."""
    __tablename__ = "wa_sessions"
    phone_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    language: Mapped[str | None] = mapped_column(String(5))
    state: Mapped[str] = mapped_column(String(20), default="AWAIT_LANG")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
