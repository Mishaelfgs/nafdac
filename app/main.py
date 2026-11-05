"""App entry point. Run: uvicorn app.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from . import jobs
from .admin.routes import router as admin_router
from .config import settings
from .db import get_db, init_db
from .whatsapp import bot
from .whatsapp.webhook import router as webhook_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_for_production()
    init_db()
    jobs.start_workers()
    yield
    await jobs.stop_workers()


app = FastAPI(title="NAFDAC Checker (independent, not NAFDAC)", lifespan=lifespan)
# SameSite=strict cookie also protects admin forms from cross-site request forgery.
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET, same_site="strict",
                   https_only=settings.is_prod, max_age=8 * 3600)
app.include_router(webhook_router)
app.include_router(admin_router)


@app.exception_handler(HTTPException)
async def http_exc(request, exc: HTTPException):
    if exc.status_code == 303:  # used by the admin login guard
        return RedirectResponse(exc.headers["Location"], status_code=303)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


@app.get("/")
def root():
    return {"service": "NAFDAC Checker", "note": "Independent checker using public data. Not NAFDAC."}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


class Simulate(BaseModel):
    phone: str
    text: str


@app.post("/dev/simulate")
def simulate(body: Simulate, db: Session = Depends(get_db)):
    """DEV ONLY: pretend a WhatsApp message arrived and see the replies, no Meta account needed."""
    if settings.is_prod:
        raise HTTPException(404)
    return {"replies": bot.handle_text(db, body.phone, body.text)}
