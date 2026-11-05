"""Admin passwords (scrypt from the Python standard library) and a tiny login throttle."""
import hashlib
import hmac
import os
import time
from collections import defaultdict

_fails: dict[str, list[float]] = defaultdict(list)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, h = stored.split("$")
        new = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1)
        return hmac.compare_digest(new.hex(), h)
    except ValueError:
        return False


def too_many_failures(ip: str, limit: int = 5, window: int = 900) -> bool:
    now = time.time()
    _fails[ip] = [t for t in _fails[ip] if now - t < window]
    return len(_fails[ip]) >= limit


def record_failure(ip: str) -> None:
    _fails[ip].append(time.time())
