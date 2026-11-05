# NAFDAC Checker (Phase 1)

WhatsApp fake-product checker for Nigeria (pilot: Ibadan). **Independent checker using public data. We are NOT NAFDAC.**
Rules baked into the code: checking is free forever; payment never touches a verdict; phone numbers are hashed.

## Stack (and why)
- **Python + FastAPI**: one language for bot, API and admin; easy for juniors to read.
- **PostgreSQL** in production (Supabase or any host), **SQLite** for local dev/tests. Same code runs on both.
- **Admin = server-rendered HTML inside FastAPI** (Jinja templates, no Node build). *Deviation from "React/Next.js":* one deployable, nothing to compile, fewer things to break in Phase 1. Phase 3's manufacturer dashboard is the right moment to move to React if you want.
- **Queue:** in-memory `asyncio.Queue` (`app/jobs.py`). Scale later with Redis + Celery/RQ; only `enqueue()` changes.
- **Fuzzy search:** `rapidfuzz` in Python (fine to ~50k products). Scale later with Postgres `pg_trgm`.

## Folder structure
```
nafdac-checker/
├── app/
│   ├── main.py               app start, /health, /dev/simulate (dev only)
│   ├── config.py db.py models.py
│   ├── jobs.py               in-memory queue + workers
│   ├── core/
│   │   ├── parsing.py        NAFDAC number normalising, batch/expiry extraction
│   │   ├── engine.py         ★ VERDICT LOGIC (read first)
│   │   ├── ratelimit.py      20 checks/hour/number + spam guard
│   │   └── privacy.py        phone hashing
│   ├── whatsapp/
│   │   ├── webhook.py        Meta webhook (verify + signature check)
│   │   ├── bot.py            session + menu flow
│   │   ├── messages.py       ALL text, 5 languages
│   │   └── client.py         sends replies via Cloud API
│   └── admin/                login, dashboard, products, reports (+ templates/)
├── db/schema.sql             generated Postgres schema
├── data/sample_products.csv  50 SAMPLE products (fictional)
├── scripts/                  seed, import_csv, create_admin, export_schema
├── tests/                    34 tests
├── Dockerfile  docker-compose.yml  .env.example
```

## Run locally (no WhatsApp account needed)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed                       # loads 50 SAMPLE products
python -m scripts.create_admin you@example.com
uvicorn app.main:app --reload
```
- Chat simulator: `curl -X POST localhost:8000/dev/simulate -H 'content-type: application/json' -d '{"phone":"2348000000000","text":"hi"}'`
  Then send `1` (English), `1`, then `SMPL-0001`. Try `SMPL-0003` (recalled), `NONE`, `Sample Paracetamol 500mg | Sample Pharma`.
- Admin: http://localhost:8000/admin/
- Tests: `python -m pytest -q`
- With Postgres: `docker compose up --build` (set `DATABASE_URL` otherwise).

## Getting WhatsApp credentials (Meta Cloud API)
1. developers.facebook.com → create a **Business** app → add the **WhatsApp** product.
2. *WhatsApp → API Setup* shows a **test phone number ID** and a temporary **access token** (24h). You can add up to 5 recipient numbers for testing.
3. For a permanent token: Business Settings → Users → **System users** → create one, assign the app, generate a token with `whatsapp_business_messaging` permission.
4. *App settings → Basic* → copy **App Secret** (`WHATSAPP_APP_SECRET`, used to verify webhook signatures).
5. Deploy (or tunnel with `ngrok http 8000`), then *WhatsApp → Configuration*: Callback URL `https://YOUR-HOST/webhook/whatsapp`, Verify token = the `WHATSAPP_VERIFY_TOKEN` you chose; subscribe to the **messages** field.
6. Set `WHATSAPP_DRY_RUN=false`. Replies inside 24h of the user's message are free-form; anything we start ourselves later (alerts) needs an approved **message template** (Phase 3).
7. A real public number needs Meta business verification and display-name approval, so start that early.

## Deploy (Render, similar on Railway)
New **Web Service** from this repo → Docker runtime → set env vars from `.env.example` (`ENV=prod`, Supabase `DATABASE_URL`, WhatsApp vars, two random secrets) → health check path `/health`. Keep **one instance** until the queue moves to Redis. Run `python -m scripts.seed` / `import_csv` and `create_admin` once from the service shell.

## Assumptions (change if wrong)
1. EXPIRED comes from the **batch expiry the user types** (`EXP 12/2026`); we have no batch database yet. `products.expiry_info` is display text only.
2. RECALLED comes from `products.status = recalled` or the `recalled_batches` table.
3. **Name only is never VERIFIED**; we ask for the NAFDAC number or manufacturer. A name match alone does not prove a pack is genuine.
4. Typed name/manufacturer only triggers SUSPICIOUS when the user clearly typed `name | maker`, so chatter cannot cause false alarms.
5. Sample numbers use the prefix `SMPL-` so they can never be mistaken for real NAFDAC numbers.
6. Pidgin/Yoruba/Hausa/Igbo texts are drafts and **need native-speaker review**.
7. Plain numbered menus (not WhatsApp buttons): works on every phone and low data.

## Phase 1 limits (coming next)
Photo/OCR and Report Fake flow (Phase 2; "Report Fake" currently says "coming soon"), report review actions, analytics, billing, manufacturer/pharmacy tools (Phase 3).
