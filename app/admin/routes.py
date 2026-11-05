"""Admin dashboard (server-rendered HTML, no JavaScript build step).
Phase 1: login, stats, products (list/add/edit), reports (view only)."""
from datetime import timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..core.parsing import format_nafdac, normalise_nafdac
from ..db import get_db
from ..models import CATEGORIES, PRODUCT_STATUSES, AdminUser, Check, Product, Report, utcnow
from .auth import record_failure, too_many_failures, verify_password

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def require_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    uid = request.session.get("admin_id")
    user = db.get(AdminUser, uid) if uid else None
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return user


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "?"
    if too_many_failures(ip):
        return templates.TemplateResponse(request, "login.html", {"error": "Too many attempts. Wait 15 minutes."}, status_code=429)
    user = db.scalar(select(AdminUser).where(AdminUser.email == email.strip().lower()))
    if not user or not verify_password(password, user.password_hash):
        record_failure(ip)
        return templates.TemplateResponse(request, "login.html", {"error": "Wrong email or password."}, status_code=401)
    request.session["admin_id"] = user.id
    return RedirectResponse("/admin/", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    week_ago = utcnow() - timedelta(days=7)
    stats = {
        "total_checks": db.scalar(select(func.count(Check.id))) or 0,
        "checks_7d": db.scalar(select(func.count(Check.id)).where(Check.created_at >= week_ago)) or 0,
        "products": db.scalar(select(func.count(Product.id))) or 0,
        "pending_reports": db.scalar(select(func.count(Report.id)).where(Report.status == "pending")) or 0,
    }
    verdicts = db.execute(select(Check.verdict, func.count()).group_by(Check.verdict).order_by(func.count().desc())).all()
    return templates.TemplateResponse(request, "dashboard.html", {"user": user, "stats": stats, "verdicts": verdicts})


@router.get("/products")
def products(request: Request, q: str = "", db: Session = Depends(get_db), user=Depends(require_admin)):
    stmt = select(Product).order_by(Product.updated_at.desc()).limit(200)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Product.product_name.ilike(like), Product.manufacturer.ilike(like),
                              Product.nafdac_number.ilike(like)))
    return templates.TemplateResponse(request, "products.html", {"user": user, "items": db.scalars(stmt).all(), "q": q})


def _form_page(request, user, product, error=None, status_code=200):
    return templates.TemplateResponse(request, "product_form.html", {
        "user": user, "p": product, "error": error, "categories": CATEGORIES, "statuses": PRODUCT_STATUSES,
    }, status_code=status_code)


def _apply_form(db: Session, product: Product, f: dict) -> str | None:
    """Validate + copy form values onto the product. Returns an error message or None."""
    key = normalise_nafdac(f["nafdac_number"])
    if not key:
        return "That does not look like a NAFDAC number (example: A4-1001)."
    if not f["product_name"].strip() or not f["manufacturer"].strip():
        return "Product name and manufacturer are required."
    if f["category"] not in CATEGORIES or f["status"] not in PRODUCT_STATUSES:
        return "Invalid category or status."
    product.product_name = f["product_name"].strip()
    product.manufacturer = f["manufacturer"].strip()
    product.nafdac_key = key
    product.nafdac_number = format_nafdac(key)
    product.category, product.status = f["category"], f["status"]
    product.pack_sizes = f["pack_sizes"].strip() or None
    product.expiry_info = f["expiry_info"].strip() or None
    product.barcode = f["barcode"].strip() or None     # optional
    product.photo_url = f["photo_url"].strip() or None
    return None


async def _read_form(request: Request) -> dict:
    form = await request.form()
    names = ("product_name", "nafdac_number", "manufacturer", "category", "pack_sizes", "status",
             "expiry_info", "barcode", "photo_url")
    return {n: str(form.get(n, "")) for n in names}


@router.get("/products/new")
def product_new(request: Request, user=Depends(require_admin)):
    return _form_page(request, user, Product(category="drug", status="active"))


@router.post("/products/new")
async def product_create(request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    f, p = await _read_form(request), Product()
    if err := _apply_form(db, p, f):
        return _form_page(request, user, p, err, 400)
    db.add(p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _form_page(request, user, p, "A product with this NAFDAC number already exists.", 400)
    return RedirectResponse("/admin/products", status_code=303)


@router.get("/products/{pid}/edit")
def product_edit(pid: int, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(404)
    return _form_page(request, user, p)


@router.post("/products/{pid}/edit")
async def product_update(pid: int, request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(404)
    if err := _apply_form(db, p, await _read_form(request)):
        db.rollback()
        return _form_page(request, user, p, err, 400)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _form_page(request, user, p, "Another product already uses this NAFDAC number.", 400)
    return RedirectResponse("/admin/products", status_code=303)


@router.get("/reports")
def reports(request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    rows = db.scalars(select(Report).order_by(Report.created_at.desc()).limit(200)).all()
    return templates.TemplateResponse(request, "reports.html", {"user": user, "items": rows})
