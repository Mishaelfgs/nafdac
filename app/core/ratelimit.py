"""Rate limiting. Two layers:
1. Checks per hour per phone (DB-backed, survives restarts). Default 20 as per project rules.
2. Message-speed spam guard (in memory, per process). If you run several servers, move this to Redis."""
import time
from collections import defaultdict, deque
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Check, utcnow

SPAM_MAX_MESSAGES = 30       # per...
SPAM_WINDOW_SECONDS = 60     # ...minute
_recent: dict[str, deque] = defaultdict(deque)


def is_rate_limited(db: Session, phone_hash: str) -> bool:
    since = utcnow() - timedelta(hours=1)
    n = db.scalar(select(func.count(Check.id)).where(Check.phone_hash == phone_hash, Check.created_at >= since))
    return (n or 0) >= settings.RATE_LIMIT_PER_HOUR


def allow_message(phone_hash: str) -> bool:
    """False = this sender is flooding us; ignore the message silently."""
    now = time.monotonic()
    q = _recent[phone_hash]
    while q and now - q[0] > SPAM_WINDOW_SECONDS:
        q.popleft()
    if len(q) >= SPAM_MAX_MESSAGES:
        return False
    q.append(now)
    return True


def reset_spam_guard() -> None:  # used by tests
    _recent.clear()
