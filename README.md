# Instagram Authentication Service

Authentication-first Render service.

Build:
`pip install -r requirements.txt`

Start:
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Endpoints:
- GET `/health`
- GET `/auth/status`
- POST `/auth/login`
- POST `/auth/verify` with `{"code":"123456"}` when 2FA is requested
- POST `/auth/logout`

Set `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` in Render Environment Variables.

For persistent sessions on Render, attach a paid persistent disk and set
`INSTAGRAM_SESSION_FILE=/var/data/instagram.json` (or another path under the disk mount).
Without a persistent disk, Render's filesystem is ephemeral.

Do not expose the auth endpoints publicly without adding API authentication.
Never commit `.env` or session files.
