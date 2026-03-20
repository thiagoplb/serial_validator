# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

`uv` is not on PATH — always invoke it via `python -m uv`.

```bash
# Run the API
python -m uv run uvicorn app.main:app --reload

# Apply migrations
python -m uv run alembic upgrade head

# Generate a migration after changing models.py
python -m uv run alembic revision --autogenerate -m "description"

# Add a dependency
python -m uv add <package>
```

## Architecture

The app separates routing from business logic: routers handle HTTP concerns, `serial_service.py` owns all validation logic.

**Request flow for `POST /validate`:**
`validate.py` → `validate_serial()` in `serial_service.py` → returns a `ValidateResponse` → router maps it to the correct HTTP status (200 / 401 / 403).

**Admin auth:** `verify_admin_key` is a FastAPI dependency in `admin.py` that reads `ADMIN_API_KEY` from `app/config.py` (loaded via `.env`). Applied via `dependencies=[Depends(verify_admin_key)]` on each route.

**DB session:** `get_db()` in `database.py` is a generator dependency injected into every route handler. The engine is SQLite with `check_same_thread=False`.

**Serial lifecycle:**
- Created by admin with optional `pre_bound_fingerprint` (for replacement serials) and `expires_at`.
- `fingerprint` column is `null` until first `POST /validate` call, which binds it permanently to that machine.
- Replacement flow: admin creates a new serial with `pre_bound_fingerprint` set to the new machine's fingerprint — validation passes only for that machine.

**`client/fingerprint.py`** is a standalone stdlib-only module (no pip dependencies) meant to be embedded in client software. `get_fingerprint()` collects MAC + disk serial + CPU identifier and returns their SHA-256 hex digest. Windows uses `wmic`, Linux uses `blkid`, with silent fallback to empty string on failure.

## Environment

`.env` (gitignored) must exist at project root:
```
ADMIN_API_KEY=<strong-key>
DATABASE_URL=sqlite:///./serials.db
```
