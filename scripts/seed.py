"""Load the 50 SAMPLE products (fake demo data). Run: python -m scripts.seed"""
from app.db import SessionLocal, init_db
from scripts.import_csv import import_csv

if __name__ == "__main__":
    init_db()
    with SessionLocal() as db:
        print(import_csv(db, "data/sample_products.csv", is_sample=True))
