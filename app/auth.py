import logging
from pathlib import Path
from typing import Optional
from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ChallengeRequired, TwoFactorRequired,
    PleaseWaitFewMinutes, LoginRequired, ReloginAttemptExceeded,
)

log = logging.getLogger("instagram-auth")

class AuthManager:
    def __init__(self, username: str, password: str, session_file: Path):
        self.username, self.password = username, password
        self.session_file = session_file
        self.client: Optional[Client] = None
        self.state = "STARTING"
        self.detail = ""
        self.exception = None

    def _client(self):
        c = Client()
        c.delay_range = [1, 3]
        return c

    def _save(self, c):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        c.dump_settings(str(self.session_file))

    def _restore(self):
        if not self.session_file.exists():
            return False
        c = self._client()
        try:
            c.load_settings(str(self.session_file))
            c.get_timeline_feed()
            self.client = c
            self.state = "AUTHENTICATED"
            self.detail = "Saved session validated."
            return True
        except Exception as e:
            log.warning("Saved session unusable: %s", type(e).__name__)
            self.client = None
            return False

    def login(self, verification_code=""):
        if self.state == "AUTHENTICATED" and self.client:
            return self.status()

        if not verification_code and self._restore():
            return self.status()

        c = self._client()
        self.state, self.detail, self.exception = "AUTHENTICATING", "Sending login request.", None

        try:
            ok = c.login(self.username, self.password,
                         verification_code=verification_code or "")
            if not ok:
                self.state, self.detail = "LOGIN_FAILED", "Instagram did not confirm login."
                return self.status()
            self.client = c
            self._save(c)
            self.state, self.detail = "AUTHENTICATED", "Authentication successful."
        except TwoFactorRequired as e:
            self.client = c
            self.state, self.detail = "TWO_FACTOR_REQUIRED", "Instagram requires a verification code."
            self.exception = type(e).__name__
        except ChallengeRequired as e:
            self.client = c
            self.state, self.detail = "CHALLENGE_REQUIRED", "Instagram requires a security challenge."
            self.exception = type(e).__name__
        except BadPassword as e:
            self.state = "LOGIN_REJECTED"
            self.detail = "Instagram rejected the login request; this is not treated as proof of a wrong password."
            self.exception = type(e).__name__
        except PleaseWaitFewMinutes as e:
            self.state, self.detail = "RATE_LIMITED", "Instagram asked the client to wait before retrying."
            self.exception = type(e).__name__
        except (ReloginAttemptExceeded, LoginRequired) as e:
            self.state, self.detail = "LOGIN_FAILED", str(e) or type(e).__name__
            self.exception = type(e).__name__
        except Exception as e:
            self.state, self.detail = "UNKNOWN_ERROR", f"{type(e).__name__}: {e}"
            self.exception = type(e).__name__
            log.exception("Unexpected authentication failure.")
        return self.status()

    def status(self):
        return {
            "state": self.state,
            "username": self.username,
            "authenticated": self.state == "AUTHENTICATED",
            "session_exists": self.session_file.exists(),
            "detail": self.detail,
            "exception": self.exception,
        }

    def logout(self):
        self.client = None
        if self.session_file.exists():
            self.session_file.unlink()
        self.state, self.detail, self.exception = "LOGGED_OUT", "Local session removed.", None
