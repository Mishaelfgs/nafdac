"""Load products from a CSV (upsert by NAFDAC number). Use this for REAL data later.

  python -m scripts.import_csv data/real_products.csv
  python -m scripts.import_csv data/sample_products.csv --sample     (marks rows as SAMPLE)

CSV columns: product_name,nafdac_number,manufacturer,category,pack_sizes,status,expiry_info,barcode,photo_url
(only product_name, nafdac_number, manufacturer, category are required; barcode may be empty)"""
import argparse
import csv

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.parsing import format_nafdac, normalise_nafdac
from app.db import SessionLocal, init_db
from app.models import CATEGORIES, PRODUCT_STATUSES, Product


def import_csv(db: Session, path: str, is_sample: bool = False) -> dict:
    stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": []}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for line_no, row in enumerate(csv.DictReader(fh), start=2):
            row = {k.strip(): (v or "").strip() for k, v in row.items() if k}
            key = normalise_nafdac(row.get("nafdac_number", ""))
            category = row.get("category", "").lower()
            status = (row.get("status") or "active").lower()
            problem = None
            if not key:
                problem = "bad NAFDAC number"
            elif not row.get("product_name") or not row.get("manufacturer"):
                problem = "missing product_name or manufacturer"
            elif category not in CATEGORIES:
                problem = f"category must be one of {CATEGORIES}"
            elif status not in PRODUCT_STATUSES:
                problem = f"status must be one of {PRODUCT_STATUSES}"
            if problem:
                stats["skipped"] += 1
                stats["errors"].append(f"line {line_no}: {problem}")
                continue
            p = db.scalar(select(Product).where(Product.nafdac_key == key))
            stats["updated" if p else "inserted"] += 1
            p = p or Product()
            p.product_name, p.manufacturer = row["product_name"], row["manufacturer"]
            p.nafdac_key, p.nafdac_number = key, format_nafdac(key)
            p.category, p.status = category, status
            p.pack_sizes = row.get("pack_sizes") or None
            p.expiry_info = row.get("expiry_info") or None
            p.barcode = row.get("barcode") or None
            p.photo_url = row.get("photo_url") or None
            p.is_sample = is_sample
            db.add(p)
    db.commit()
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--sample", action="store_true", help="mark rows as SAMPLE data")
    args = ap.parse_args()
    init_db()
    with SessionLocal() as session:
        result = import_csv(session, args.csv_path, args.sample)
    print({k: v for k, v in result.items() if k != "errors"})
    for e in result["errors"]:
        print("  ", e)
