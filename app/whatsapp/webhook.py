"""Meta WhatsApp Cloud API webhook: GET = one-time verification, POST = incoming messages."""
import hashlib
import hmac
import json
import logging
from collections import OrderedDict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from ..config import settings
from ..jobs import IncomingMessage, enqueue

log = logging.getLogger("webhook")
router = APIRouter()

_seen: OrderedDict[str, None] = OrderedDict()   # Meta retries deliveries; skip message ids we already handled


def verify_signature(body: bytes, header: str | None, secret: str) -> bool:
    """Meta signs each POST with HMAC-SHA256 of the raw body using your App Secret."""
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.split("=", 1)[1])


def _already_seen(msg_id: str) -> bool:
    if msg_id in _seen:
        return True
    _seen[msg_id] = None
    while len(_seen) > 5000:
        _seen.popitem(last=False)
    return False


def extract_messages(payload: dict) -> list[tuple[str, str, IncomingMessage]]:
    """Pull (message_id, ..., IncomingMessage) out of Meta's nested payload."""
    out = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for m in change.get("value", {}).get("messages", []) or []:
                kind = m.get("type", "other")
                body = m.get("text", {}).get("body", "") if kind == "text" else ""
                out.append((m.get("id", ""), kind, IncomingMessage(phone=m.get("from", ""), kind=kind, body=body)))
    return out


@router.get("/webhook/whatsapp")
async def verify(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and settings.WHATSAPP_VERIFY_TOKEN \
            and hmac.compare_digest(q.get("hub.verify_token", ""), settings.WHATSAPP_VERIFY_TOKEN):
        return PlainTextResponse(q.get("hub.challenge", ""))
    raise HTTPException(403, "Verification failed")


@router.post("/webhook/whatsapp")
async def receive(request: Request):
    body = await request.body()
    if settings.WHATSAPP_APP_SECRET:
        if not verify_signature(body, request.headers.get("X-Hub-Signature-256"), settings.WHATSAPP_APP_SECRET):
            raise HTTPException(403, "Bad signature")
    elif settings.is_prod:
        raise HTTPException(500, "WHATSAPP_APP_SECRET not set")
    try:
        payload = json.loads(body)
    except ValueError:
        raise HTTPException(400, "Invalid JSON")
    for msg_id, _kind, msg in extract_messages(payload):
        if msg.phone and not (msg_id and _already_seen(msg_id)):
            enqueue(msg)
    return {"status": "ok"}   # always 200 fast, otherwise Meta keeps retrying
