import logging
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    TwoFactorRequired,
)

log = logging.getLogger("instagram-auth")


class InstagramAuth:
    def __init__(self, username: str, password: str, session_file: Path):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.client = Client()

    def _load_session(self) -> bool:
        if not self.session_file.exists():
            return False

        try:
            self.client.load_settings(str(self.session_file))
            log.info("Saved session loaded.")
            return True
        except Exception as exc:
            log.warning("Saved session could not be loaded: %s", type(exc).__name__)
            return False

    def _save_session(self) -> None:
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.client.dump_settings(str(self.session_file))
        log.info("Authenticated session saved.")

    def login(self) -> Client:
        loaded = self._load_session()

        if loaded:
            try:
                self.client.get_timeline_feed()
                log.info("Session is valid; login not required.")
                return self.client
            except Exception as exc:
                log.warning(
                    "Saved session is not usable; performing fresh login: %s",
                    type(exc).__name__,
                )

        try:
            log.info("Starting Instagram login for %s", self.username)
            self.client.login(self.username, self.password)
            self._save_session()
            log.info("Instagram authentication successful.")
            return self.client

        except TwoFactorRequired:
            raise RuntimeError(
                "Instagram requested 2FA. The initial prototype needs an "
                "interactive 2FA handler before this login can complete."
            ) from None

        except ChallengeRequired:
            raise RuntimeError(
                "Instagram requested a login challenge/checkpoint. "
                "Complete the verification in Instagram, then retry."
            ) from None

        except BadPassword:
            raise RuntimeError("Instagram rejected the supplied credentials.") from None

        except Exception as exc:
            raise RuntimeError(
                f"Instagram login failed: {type(exc).__name__}: {exc}"
            ) from exc

    def status(self) -> dict:
        return {
            "username": self.username,
            "session_exists": self.session_file.exists(),
            "session_file": str(self.session_file),
        }
