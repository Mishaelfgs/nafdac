"""Chat flow (session handling + menu). No WhatsApp network calls here: it takes text in and
returns a list of reply strings, which makes it easy to test.

States:  AWAIT_LANG -> MENU -> AWAIT_CHECK -> (verdict) -> MENU ...
After every verdict we go back to MENU, so "2" (report) always means "report", not "check '2'".
"""
from sqlalchemy.orm import Session

from ..core.engine import check_input
from ..core.privacy import hash_phone
from ..core.ratelimit import allow_message, is_rate_limited
from ..models import Check, WaSession
from .messages import LANG_CHOICES, LANG_MENU, render_verdict, t


def _session(db: Session, ph: str) -> WaSession:
    s = db.get(WaSession, ph)
    if not s:
        s = WaSession(phone_hash=ph, state="AWAIT_LANG")
        db.add(s)
    return s


def _run_check(db: Session, ph: str, lang: str, text: str) -> list[str]:
    if is_rate_limited(db, ph):
        return [t(lang, "rate_limited")]
    result = check_input(db, text)
    db.add(Check(
        phone_hash=ph, input_type=result.input_type, input_text=text[:200], verdict=result.verdict.value,
        product_id=result.product.id if result.product else None, language=lang,
    ))
    return [render_verdict(lang, result)]


def handle_text(db: Session, phone: str, text: str) -> list[str]:
    """Process one incoming text message. Returns the replies to send (maybe none)."""
    ph = hash_phone(phone)
    if not allow_message(ph):
        return []  # flooding: ignore silently
    s = _session(db, ph)
    raw = (text or "").strip()
    cmd = raw.upper()
    try:
        # Language selection (first contact, or user sent LANG)
        if cmd == "LANG":
            s.state = "AWAIT_LANG"
            return [LANG_MENU]
        if s.language is None or s.state == "AWAIT_LANG":
            if cmd in LANG_CHOICES:
                s.language, s.state = LANG_CHOICES[cmd], "MENU"
                return [t(s.language, "menu")]
            s.state = "AWAIT_LANG"
            return [LANG_MENU]

        lang = s.language
        if cmd in ("MENU", "HI", "HELLO", "START", "HOME"):
            s.state = "MENU"
            return [t(lang, "menu")]
        if cmd == "HELP":
            return [t(lang, "help")]

        if s.state == "MENU":
            if cmd == "1":
                s.state = "AWAIT_CHECK"
                return [t(lang, "ask_check")]
            if cmd == "2":
                return [t(lang, "report_soon")]   # Phase 2: real report flow
            if cmd == "3":
                return [t(lang, "help")]
            if len(raw) < 3:
                return [t(lang, "menu")]
            # Anything longer is treated as a product to check (fast path for traders)

        replies = _run_check(db, ph, lang, raw)
        s.state = "MENU"
        return replies
    finally:
        db.commit()


def handle_image(db: Session, phone: str) -> list[str]:
    """Photo checks arrive in Phase 2 (OCR). For now ask for the typed number."""
    ph = hash_phone(phone)
    s = _session(db, ph)
    db.commit()
    return [t(s.language or "en", "photo_later")]
