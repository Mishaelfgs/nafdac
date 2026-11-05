from app.models import Product
from scripts.import_csv import import_csv
from sqlalchemy import func, select


def test_sample_csv_imports_50_and_is_idempotent(Session):
    with Session() as db:
        r = import_csv(db, "data/sample_products.csv", is_sample=True)
        assert r["inserted"] == 50 and not r["errors"]
        assert import_csv(db, "data/sample_products.csv", is_sample=True)["updated"] == 50
        assert db.scalar(select(func.count(Product.id)).where(Product.is_sample.is_(True))) == 50
