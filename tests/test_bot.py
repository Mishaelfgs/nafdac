from sqlalchemy import select

from app.models import Check, WaSession
from app.whatsapp import bot
from app.whatsapp.messages import LANG_MENU

PHONE = "2348012345678"


def test_language_flow_and_check(db):
    assert bot.handle_text(db, PHONE, "hi") == [LANG_MENU]
    assert "Check a product" in bot.handle_text(db, PHONE, "1")[0]
    assert "Send ONE" in bot.handle_text(db, PHONE, "1")[0]
    out = bot.handle_text(db, PHONE, "SMPL-0001")[0]
    assert "VERIFIED" in out and "We are NOT NAFDAC" in out         # disclaimer on every verdict
    assert "SAMPLE" in out


def test_pidgin_reply(db):
    bot.handle_text(db, PHONE, "hello"); bot.handle_text(db, PHONE, "2")
    assert "NO DEY FOR RECORD" in bot.handle_text(db, PHONE, "SMPL-9999")[0]


def test_every_language_has_every_key():
    from app.whatsapp.messages import TEXT
    base = set(TEXT["en"])
    for lang, d in TEXT.items():
        assert set(d) == base, lang


def test_fast_path_and_report_option_after_verdict(db):
    bot.handle_text(db, PHONE, "hi"); bot.handle_text(db, PHONE, "1")
    bot.handle_text(db, PHONE, "SMPL-0001")
    assert "coming very soon" in bot.handle_text(db, PHONE, "2")[0]  # "2" means report, not "check 2"


def test_phone_never_stored_raw(db):
    bot.handle_text(db, PHONE, "hi"); bot.handle_text(db, PHONE, "1"); bot.handle_text(db, PHONE, "SMPL-0001")
    for c in db.scalars(select(Check)):
        assert PHONE not in (c.phone_hash + (c.input_text or ""))
    for s in db.scalars(select(WaSession)):
        assert PHONE not in s.phone_hash


def test_rate_limit_20_per_hour(db):
    bot.handle_text(db, PHONE, "hi"); bot.handle_text(db, PHONE, "1")
    for _ in range(20):
        assert "VERIFIED" in bot.handle_text(db, PHONE, "SMPL-0001")[0]
    assert "limit of 20" in bot.handle_text(db, PHONE, "SMPL-0001")[0]


def test_image_asks_for_typed_number(db):
    assert "type" in bot.handle_image(db, PHONE)[0].lower()
