"""THE BRAIN: decides the verdict. Read this file first if you are new to the project.

Order of decisions (safety first):
  1. User says pack has NO NAFDAC number           -> SUSPICIOUS
  2. NAFDAC number given:
       not in DB                                    -> NOT_FOUND (+ "did you mean" for 1-character typos)
       in DB:  recalled -> RECALLED
               batch expiry in the past -> EXPIRED
               suspended -> SUSPICIOUS
               name/manufacturer typed and conflicting -> SUSPICIOUS
               otherwise -> VERIFIED
  3. No number, but product name (+ manufacturer):
       name AND manufacturer both match -> same checks as above (VERIFIED etc.)
       name matches but manufacturer does not -> SUSPICIOUS
       name only -> NEED_MORE_INFO (a name alone does not prove a pack is genuine)
       nothing close -> NOT_FOUND
  4. Anything else (too little to go on) -> NEED_MORE_INFO

Barcode is never required. Payment status is never looked at: nothing here can be bought.
"""
import re
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from rapidfuzz import fuzz, process
from rapidfuzz.distance import Levenshtein
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Product, RecalledBatch
from .parsing import ParsedInput, parse_message


class Verdict(str, Enum):
    VERIFIED = "VERIFIED"
    NOT_FOUND = "NOT_FOUND"
    EXPIRED = "EXPIRED"
    RECALLED = "RECALLED"
    SUSPICIOUS = "SUSPICIOUS"
    NEED_MORE_INFO = "NEED_MORE_INFO"


@dataclass
class CheckResult:
    verdict: Verdict
    input_type: str
    product: Product | None = None
    reasons: list[str] = field(default_factory=list)       # machine-readable, for logs/admin
    suggestions: list[Product] = field(default_factory=list)


# Fuzzy-match thresholds (0-100). Tune with real data.
NAME_MATCH = 85       # name is "the same product"
NAME_SIMILAR = 60     # name is "something like it" (we only suggest, never verify)
MAKER_MATCH = 75      # manufacturer is "the same company"
CONFLICT_NAME = 50    # below this, a typed name clearly contradicts the record
CONFLICT_MAKER = 55   # below this, a typed manufacturer clearly contradicts the record


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()


def _score(a: str, b: str) -> float:
    return fuzz.WRatio(_clean(a), _clean(b))


def _judge_registered(db: Session, product: Product, parsed: ParsedInput, today: date,
                      check_conflict: bool) -> tuple[Verdict, list[str]]:
    """Product exists. Decide between RECALLED / EXPIRED / SUSPICIOUS / VERIFIED."""
    if product.status == "recalled":
        return Verdict.RECALLED, ["product_recalled"]
    if parsed.batch and db.scalar(select(RecalledBatch.id).where(
            RecalledBatch.product_id == product.id, RecalledBatch.batch_no == parsed.batch.upper())):
        return Verdict.RECALLED, ["batch_recalled"]
    if parsed.expiry and parsed.expiry < today:
        return Verdict.EXPIRED, ["batch_expired"]
    if product.status == "suspended":
        return Verdict.SUSPICIOUS, ["product_suspended"]
    # Only compare typed name/manufacturer if the user clearly typed "name | maker" (2 parts),
    # so chatter like "please check this" can never cause a false SUSPICIOUS.
    if check_conflict and parsed.explicit_parts >= 2:
        if parsed.name and _score(parsed.name, product.product_name) < CONFLICT_NAME:
            return Verdict.SUSPICIOUS, ["name_mismatch"]
        if parsed.manufacturer and _score(parsed.manufacturer, product.manufacturer) < CONFLICT_MAKER:
            return Verdict.SUSPICIOUS, ["maker_mismatch"]
    return Verdict.VERIFIED, []


def _near_keys(db: Session, key: str, limit: int = 3) -> list[Product]:
    """Products whose NAFDAC key differs from `key` by exactly one character (likely a typo)."""
    keys = db.scalars(select(Product.nafdac_key)).all()
    close = [k for k in keys if k != key and Levenshtein.distance(k, key) <= 1][:limit]
    if not close:
        return []
    return list(db.scalars(select(Product).where(Product.nafdac_key.in_(close))))


def _search_by_name(db: Session, name: str, limit: int = 5) -> list[tuple[Product, float]]:
    """Fuzzy name search. MVP loads names into memory (fine up to ~50k products).
    To scale: use PostgreSQL pg_trgm (similarity()) with a GIN index instead."""
    rows = db.execute(select(Product.id, Product.product_name)).all()
    choices = {r.id: _clean(r.product_name) for r in rows}
    hits = process.extract(_clean(name), choices, scorer=fuzz.WRatio, limit=limit, score_cutoff=NAME_SIMILAR)
    if not hits:
        return []
    products = {p.id: p for p in db.scalars(select(Product).where(Product.id.in_([h[2] for h in hits])))}
    return [(products[h[2]], h[1]) for h in hits]


def check_input(db: Session, text: str, today: date | None = None) -> CheckResult:
    today = today or date.today()
    parsed = parse_message(text)

    # 1. Pack has no NAFDAC number at all
    if parsed.no_number and not parsed.nafdac_key:
        return CheckResult(Verdict.SUSPICIOUS, "no_number", reasons=["no_nafdac_on_pack"])

    # 2. NAFDAC number path (primary key lookup)
    if parsed.nafdac_key:
        product = db.scalar(select(Product).where(Product.nafdac_key == parsed.nafdac_key))
        if not product:
            return CheckResult(Verdict.NOT_FOUND, "nafdac_number", reasons=["number_not_in_db"],
                               suggestions=_near_keys(db, parsed.nafdac_key))
        verdict, reasons = _judge_registered(db, product, parsed, today, check_conflict=True)
        return CheckResult(verdict, "nafdac_number", product=product, reasons=reasons)

    # 3. Name (+ manufacturer) fallback
    if parsed.name and len(_clean(parsed.name)) >= 3:
        hits = _search_by_name(db, parsed.name)
        if not hits:
            return CheckResult(Verdict.NOT_FOUND, "product_name", reasons=["name_not_in_db"])
        strong = [(p, s) for p, s in hits if s >= NAME_MATCH]
        if not strong:
            return CheckResult(Verdict.NEED_MORE_INFO, "product_name", reasons=["similar_only"],
                               suggestions=[p for p, _ in hits[:3]])
        if not parsed.manufacturer:
            return CheckResult(Verdict.NEED_MORE_INFO, "product_name", reasons=["name_only"],
                               suggestions=[p for p, _ in strong[:3]])
        matched = [(p, s) for p, s in strong if _score(parsed.manufacturer, p.manufacturer) >= MAKER_MATCH]
        if not matched:
            return CheckResult(Verdict.SUSPICIOUS, "product_name", product=strong[0][0], reasons=["maker_mismatch"])
        product = matched[0][0]
        verdict, reasons = _judge_registered(db, product, parsed, today, check_conflict=False)
        return CheckResult(verdict, "product_name", product=product, reasons=reasons)

    # 4. Not enough to go on (e.g. only a batch number, or gibberish)
    return CheckResult(Verdict.NEED_MORE_INFO, "unreadable", reasons=["no_identifier"])
