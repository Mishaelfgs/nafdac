"""Simple in-memory queue so the webhook can answer Meta instantly (<1s) while checks run in workers.

MVP limits: jobs are lost if the server restarts, and it only works on ONE server process.
To scale: replace with Redis + Celery/RQ (Python) or BullMQ (Node). Keep `enqueue()` as the only entry point
and the rest of the app will not change."""
import asyncio
import logging
from dataclasses import dataclass

from .db import SessionLocal
from .whatsapp import bot
from .whatsapp.client import send_text
from .whatsapp.messages import t

log = logging.getLogger("jobs")


@dataclass
class IncomingMessage:
    phone: str          # raw number, kept ONLY in memory while we reply; never stored
    kind: str           # "text" | "image" | other
    body: str = ""


_queue: asyncio.Queue | None = None
_workers: list[asyncio.Task] = []


def _process(msg: IncomingMessage) -> list[str]:
    """Runs in a thread (database calls are blocking)."""
    with SessionLocal() as db:
        if msg.kind == "text":
            return bot.handle_text(db, msg.phone, msg.body)
        if msg.kind == "image":
            return bot.handle_image(db, msg.phone)
        return [t("en", "menu")]  # stickers, audio, etc.: just show the menu


async def _worker() -> None:
    assert _queue is not None
    while True:
        msg = await _queue.get()
        try:
            for reply in await asyncio.to_thread(_process, msg):
                await send_text(msg.phone, reply)
        except Exception:  # never let one bad message kill the worker
            log.exception("Failed to process message")
            try:
                await send_text(msg.phone, t("en", "error"))
            except Exception:
                log.exception("Could not send error message")
        finally:
            _queue.task_done()


def start_workers(n: int = 4) -> None:
    global _queue
    _queue = asyncio.Queue(maxsize=1000)
    _workers.extend(asyncio.create_task(_worker()) for _ in range(n))


async def stop_workers() -> None:
    for w in _workers:
        w.cancel()
    _workers.clear()


def enqueue(msg: IncomingMessage) -> bool:
    """False if the queue is full (we drop the message rather than crash)."""
    if _queue is None:
        raise RuntimeError("Workers not started")
    try:
        _queue.put_nowait(msg)
        return True
    except asyncio.QueueFull:
        log.error("Queue full, dropping message")
        return False
