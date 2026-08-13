# Instagram Authentication Bot

Minimal authentication-first prototype.

## 1. Install

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

## 2. Configure

Copy `.env.example` to `.env` and fill in:

- `INSTAGRAM_USERNAME`
- `INSTAGRAM_PASSWORD`

Never commit `.env`.

## 3. Run

```bash
python -m app.main
```

A successful login creates a local authenticated session under `sessions/`.

Check configuration/session state:

```bash
python -m app.main status
```

## Authentication behavior

The program first tries a saved session. If it is absent or unusable, it performs a username/password login.

Instagram may require 2FA or a security challenge. This prototype reports those states explicitly rather than attempting to bypass them.

## Security

- Credentials are loaded from `.env`.
- Passwords are never printed.
- Session files are ignored by Git.
- Do not upload `.env` or session files to GitHub.
