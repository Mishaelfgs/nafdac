import hashlib
import hmac

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from app.admin.auth import hash_password
from app.admin.routes import router as admin_router
from app.db import get_db
from app.models import AdminUser
from app.whatsapp.webhook import extract_messages, verify_signature


def test_signature():
    body, secret = b'{"a":1}', "s3cret"
    good = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_signature(body, good, secret)
    assert not verify_signature(body, "sha256=bad", secret) and not verify_signature(body, None, secret)


def test_extract_messages():
    payload = {"entry": [{"changes": [{"value": {"messages": [
        {"from": "234801", "id": "wamid.1", "type": "text", "text": {"body": "hi"}}]}}]}]}
    (mid, kind, msg), = extract_messages(payload)
    assert (mid, kind, msg.phone, msg.body) == ("wamid.1", "text", "234801", "hi")


def test_admin_login_and_pages(Session, db):
    db.add(AdminUser(email="a@b.com", password_hash=hash_password("longpassword1"))); db.commit()
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="x")
    app.include_router(admin_router)
    app.dependency_overrides[get_db] = lambda: db
    c = TestClient(app, follow_redirects=False)
    assert c.get("/admin/").status_code == 303                      # not logged in -> redirect
    assert c.post("/admin/login", data={"email": "a@b.com", "password": "wrong"}).status_code == 401
    assert c.post("/admin/login", data={"email": "a@b.com", "password": "longpassword1"}).status_code == 303
    assert c.get("/admin/").status_code == 200
    assert "Sample Paracetamol" in c.get("/admin/products").text
    r = c.post("/admin/products/new", data={"product_name": "New Item", "nafdac_number": "A4-5555", "manufacturer": "X Ltd",
                                            "category": "food", "status": "active", "pack_sizes": "", "expiry_info": "",
                                            "barcode": "", "photo_url": ""})
    assert r.status_code == 303
    dup = c.post("/admin/products/new", data={"product_name": "Dup", "nafdac_number": "A4-5555", "manufacturer": "Y",
                                              "category": "food", "status": "active", "pack_sizes": "", "expiry_info": "",
                                              "barcode": "", "photo_url": ""})
    assert dup.status_code == 400 and "already exists" in dup.text
