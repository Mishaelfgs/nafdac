"""Sends messages through the Meta WhatsApp Cloud API. In dry-run mode it only logs (local dev)."""
import logging

import httpx

from ..config import settings

log = logging.getLogger("whatsapp")


async def send_text(to: str, body: str) -> None:
    if settings.WHATSAPP_DRY_RUN:
        log.info("[DRY RUN] to=***%s\n%s", to[-4:], body)
        return
    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient(timeout=15) as client:
        for attempt in (1, 2):  # one retry on temporary failure
            resp = await client.post(url, json=payload, headers=headers)
            if resp.status_code < 500:
                if resp.status_code >= 400:
                    log.error("WhatsApp send failed %s: %s", resp.status_code, resp.text[:300])
                return
            log.warning("WhatsApp 5xx on attempt %s", attempt)
