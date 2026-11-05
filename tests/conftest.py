import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.ratelimit import reset_spam_guard
from app.db import Base
from app.models import Product, RecalledBatch


@pytest.fixture()
def Session():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    reset_spam_guard()
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture()
def db(Session):
    with Session() as s:
        def add(name, key, maker, status="active", barcode=None):
            from app.core.parsing import format_nafdac
            p = Product(product_name=name, nafdac_number=format_nafdac(key), nafdac_key=key, manufacturer=maker,
                        category="drug", status=status, barcode=barcode, is_sample=True)
            s.add(p)
            return p
        add("Sample Paracetamol 500mg Tablets", "SMPL0001", "Sample Pharma Ltd")            # no barcode
        add("Sample Ibuprofen 400mg Tablets", "SMPL0002", "Demo Healthcare Nigeria Ltd", barcode="123456")
        rec = add("Sample Recalled Syrup", "SMPL0003", "Example Labs Ltd", status="recalled")
        batchy = add("Sample Batchy Tablets", "A41001", "Example Labs Ltd")
        s.flush()
        s.add(RecalledBatch(product_id=batchy.id, batch_no="BAD99", reason="test"))
        s.commit()
        yield s
