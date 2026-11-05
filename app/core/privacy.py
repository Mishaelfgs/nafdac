"""Privacy helpers (NDPC principles: data minimisation). We never store raw phone numbers."""
import hashlib
import hmac
import re

from ..config import settings


def hash_phone(phone: str) -> str:
    """One-way salted hash. Same phone -> same hash (for rate limits), but cannot be reversed."""
    digits = re.sub(r"\D", "", phone)
    return hmac.new(settings.PHONE_HASH_SALT.encode(), digits.encode(), hashlib.sha256).hexdigest()
