"""Turn messy WhatsApp text into structured input. Pure functions: no database here.

NAFDAC numbers look like  A4-1001, B1-0123, 01-2001, 04-1234  (prefix + digits).
We normalise to a "key" with no spaces/dashes (A41001) so "a4 1001" and "A4-1001" match.
"""
import calendar
import re
from dataclasses import dataclass
from datetime import date

# Common typing/OCR mistakes inside the DIGIT part of a number: letter O for zero, etc.
_DIGIT_FIX = str.maketrans({"O": "0", "Q": "0", "I": "1", "L": "1", "S": "5", "B": "8"})


def _fix_digits(s: str) -> str:
    return s.translate(_DIGIT_FIX)


def normalise_nafdac(raw: str) -> str | None:
    """'a4 - 1001' -> 'A41001'. Returns None if it cannot be a NAFDAC number.
    'SMPL' prefix is used only by our SAMPLE data so it can never be mistaken for a real number."""
    clean = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if clean.startswith("NAFDAC"):
        clean = clean[6:]
    if len(clean) < 5:
        return None
    if clean.startswith("SMPL"):
        prefix, rest = "SMPL", _fix_digits(clean[4:])
    elif clean[0] in "OQIL" or clean[0].isdigit():       # two-digit prefix, e.g. 01-2001
        prefix, rest = _fix_digits(clean[:2]), _fix_digits(clean[2:])
        if not prefix.isdigit():
            return None
    elif clean[0].isalpha():                              # letter+digit prefix, e.g. A4-1001
        prefix, rest = clean[0] + _fix_digits(clean[1:2]), _fix_digits(clean[2:])
        if not prefix[1].isdigit():
            return None
    else:
        return None
    if not (rest.isdigit() and 3 <= len(rest) <= 6):
        return None
    return prefix + rest


def format_nafdac(key: str) -> str:
    """'A41001' -> 'A4-1001' (for display only)."""
    n = 4 if key.startswith("SMPL") else 2
    return f"{key[:n]}-{key[n:]}"


# A candidate number inside a sentence. Needs >=3 real digits (checked below) to avoid matching words.
_TOKEN = re.compile(
    r"(?<![A-Z0-9])(?:SMPL|[A-Z][0-9OIL]|[0-9OIL]{2})[\s\-]?[0-9OILSB]{3,6}(?![A-Z0-9])"
)


def find_nafdac(text: str) -> tuple[str, tuple[int, int]] | None:
    """Find the first NAFDAC-looking number. Returns (key, (start, end)) or None."""
    for m in _TOKEN.finditer(text.upper()):
        if sum(c.isdigit() for c in m.group()) < 3:
            continue
        key = normalise_nafdac(m.group())
        if key:
            return key, m.span()
    return None


_MONTHS = {n.upper(): i for i, n in enumerate(calendar.month_abbr) if n}


def _eom(y: int, m: int) -> date:
    return date(y, m, calendar.monthrange(y, m)[1])  # expiry "12/2026" means end of Dec 2026


def _date_in(text: str):
    """Find a date in text. Returns (date, (start, end)) or None. Month/year dates -> last day of month."""
    up = text.upper()
    try:
        if m := re.search(r"(\d{1,2})[/\-. ](\d{1,2})[/\-. ](\d{4})", up):          # 31/12/2026
            return date(int(m[3]), int(m[2]), int(m[1])), m.span()
        if m := re.search(r"(?<!\d)(\d{1,2})[/\-.](\d{4})(?!\d)", up):               # 12/2026
            return _eom(int(m[2]), int(m[1])), m.span()
        if m := re.search(r"(?<!\d)(\d{4})[/\-.](\d{1,2})(?!\d)", up):               # 2026-12
            return _eom(int(m[1]), int(m[2])), m.span()
        if m := re.search(r"\b([A-Z]{3})[A-Z]*[\s,./\-]*(\d{4}|\d{2})\b", up):       # DEC 2026
            mon = _MONTHS.get(m[1])
            if mon:
                y = int(m[2]) + (2000 if len(m[2]) == 2 else 0)
                return _eom(y, mon), m.span()
        if m := re.search(r"(?<!\d)(\d{1,2})[/\-.](\d{2})(?!\d)", up):               # 12/26
            return _eom(2000 + int(m[2]), int(m[1])), m.span()
    except ValueError:  # e.g. month 13
        return None
    return None


def parse_expiry(text: str) -> date | None:
    res = _date_in(text)
    return res[0] if res else None


_BATCH = re.compile(r"\b(?:BATCH|BN|LOT)\b\s*(?:NO\.?|NUMBER|#)?\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-/]{1,19})")
# Expiry is only read after an EXP keyword, because "01-2001" is also a valid NAFDAC number format.
_EXP = re.compile(r"\bEXP(?:IRY|IRES|IRATION)?\b\.?\s*(?:DATE)?\s*[:\-]?\s*")
_FILLER = re.compile(r"\b(NAFDAC|REG(?:ISTRATION)?|NO|NUMBER)\b\.?:?", re.I)
_SPLIT = re.compile(r"[|\n,;]|\s+by\s+", re.I)


@dataclass
class ParsedInput:
    raw: str
    nafdac_key: str | None = None
    name: str | None = None
    manufacturer: str | None = None
    batch: str | None = None
    expiry: date | None = None
    no_number: bool = False       # user says the pack has no NAFDAC number
    explicit_parts: int = 0       # how many "name | maker" parts the user typed


def _blank(s: str, spans: list[tuple[int, int]]) -> str:
    chars = list(s)
    for a, b in spans:
        chars[a:b] = " " * (b - a)
    return "".join(chars)


def parse_message(text: str) -> ParsedInput:
    s = (text or "").strip()
    up = s.upper()
    p = ParsedInput(raw=s)
    spans: list[tuple[int, int]] = []

    if re.search(r"\bNO\s+(NAFDAC|NUMBER)\b", up) or re.fullmatch(r"\W*(NONE|0)\W*", up):
        p.no_number = True
    if m := _BATCH.search(up):
        p.batch = m[1]
        spans.append(m.span())
    if m := _EXP.search(up):
        res = _date_in(up[m.end(): m.end() + 16])
        if res:
            p.expiry = res[0]
            spans.append((m.start(), m.end() + res[1][1]))

    working = _blank(s, spans)
    if found := find_nafdac(working):
        p.nafdac_key = found[0]
        working = _blank(working, [found[1]])

    parts = [_FILLER.sub(" ", x).strip(" .:-\t") for x in _SPLIT.split(working)]
    parts = [re.sub(r"\s+", " ", x) for x in parts if len(x.strip(" .:-")) >= 2]
    p.explicit_parts = len(parts)
    if parts:
        p.name = parts[0]
    if len(parts) > 1:
        p.manufacturer = parts[1]
    return p
