# Serial Validator

A REST API for serial key authentication with machine fingerprint binding. Prevents a single serial from being used on multiple machines simultaneously.

---

## How It Works

1. The **admin** creates serial keys via the API.
2. The **client software** collects a hardware fingerprint from the end user's machine and sends it alongside the serial key to `POST /validate`.
3. On first validation, the serial is permanently bound to that machine's fingerprint.
4. Subsequent validations from the same machine succeed; any other machine is rejected.

---

## Server Setup

### Prerequisites

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) (installed as a Python module)

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd SerialValidator
python -m uv sync
```

### 2. Configure environment

Create a `.env` file at the project root:

```env
ADMIN_API_KEY=your-strong-secret-key-here
DATABASE_URL=sqlite:///./serials.db
```

`ADMIN_API_KEY` is the key required for all admin endpoints. Use a long, random string.

### 3. Apply database migrations

```bash
python -m uv run alembic upgrade head
```

This creates `serials.db` with the required schema.

### 4. Run the API

```bash
python -m uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## Admin Endpoints

All admin endpoints require the header `X-Admin-Key: <your ADMIN_API_KEY>`.

### Create a serial

```
POST /admin/serials
```

Request body (all fields optional):

```json
{
  "serial_key": "MY-CUSTOM-KEY-001",
  "pre_bound_fingerprint": null,
  "expires_at": null
}
```

- `serial_key`: if omitted, a random key is generated automatically.
- `pre_bound_fingerprint`: pre-authorize a specific machine fingerprint (used for replacement serials — see below).
- `expires_at`: ISO 8601 datetime after which the serial stops being valid (e.g. `"2026-12-31T23:59:59"`).

### List all serials

```
GET /admin/serials
```

### Get a specific serial

```
GET /admin/serials/{serial_id}
```

### Revoke a serial

```
PATCH /admin/serials/{serial_id}/revoke
```

Sets `is_active` to `false`. The serial will be permanently rejected on validation.

---

## Validation Endpoint

This is the endpoint called by client software.

```
POST /validate
```

Request body:

```json
{
  "serial_key": "MY-CUSTOM-KEY-001",
  "fingerprint": "<sha256 hex digest from client>"
}
```

Response codes and payloads:

| Status | `valid` | `message`                           | Cause                                      |
|--------|---------|-------------------------------------|--------------------------------------------|
| 200    | `true`  | —                                                     | Valid serial, correct machine              |
| 401    | `false` | `"Invalid serial"`                                    | Serial key does not exist                  |
| 403    | `false` | `"Serial revoked"`                                    | Serial was revoked by admin                |
| 403    | `false` | `"Serial expired"`                                    | Serial is past its expiry date             |
| 403    | `false` | `"Unauthorized machine"`                              | `pre_bound_fingerprint` set, wrong machine |
| 403    | `false` | `"Serial already activated on another machine"`       | Serial already bound to a different machine |

---

## Client Integration

### 1. Copy the fingerprint module

Copy `client/fingerprint.py` into your project. It has **no external dependencies** — only Python stdlib.

```
your-project/
└── fingerprint.py   ← copy this file
```

### 2. Collect the fingerprint and validate

```python
from fingerprint import get_fingerprint
import urllib.request
import json

def validate_license(serial_key: str) -> bool:
    fingerprint = get_fingerprint()
    payload = json.dumps({
        "serial_key": serial_key,
        "fingerprint": fingerprint
    }).encode()

    req = urllib.request.Request(
        "https://your-api-host/validate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200
    except urllib.error.HTTPError:
        return False
```

Call `validate_license()` at your software's startup. If it returns `False`, deny access.

### How `get_fingerprint()` works

It collects three hardware identifiers from the machine:

- MAC address (via `uuid.getnode()`)
- Disk serial number (`wmic` on Windows, `blkid` on Linux)
- CPU identifier (`platform.processor()`)

These are concatenated and hashed with SHA-256. The resulting hex digest is stable across reboots as long as the hardware does not change.

---

## Replacement Serial Flow

When a customer gets a new machine, the admin creates a replacement serial pre-authorized for the new machine:

1. Obtain the new machine's fingerprint (have the customer run `get_fingerprint()` and send you the output).
2. Create a new serial with `pre_bound_fingerprint` set to that fingerprint:

```json
POST /admin/serials
{
  "pre_bound_fingerprint": "<new machine fingerprint>"
}
```

3. Send the new serial key to the customer.
4. On first validation from the new machine, the serial binds permanently to it.
5. Optionally revoke the old serial.

---

## Adding Migrations After Model Changes

If you modify `app/models.py`, generate and apply a new migration:

```bash
python -m uv run alembic revision --autogenerate -m "describe your change"
python -m uv run alembic upgrade head
```
