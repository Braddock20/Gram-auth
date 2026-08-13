import logging
import sys

from .config import load_settings
from .instagram_auth import InstagramAuth


def main() -> int:
    settings = load_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    auth = InstagramAuth(
        username=settings.username,
        password=settings.password,
        session_file=settings.session_file,
    )

    if len(sys.argv) > 1 and sys.argv[1].lower() == "status":
        print(auth.status())
        return 0

    try:
        client = auth.login()

        # Minimal proof that we have an authenticated client.
        print("AUTHENTICATED")
        print(f"username={settings.username}")
        print(f"session_saved={settings.session_file.exists()}")
        print(f"client_ready={client is not None}")
        return 0

    except RuntimeError as exc:
        logging.getLogger("instagram-auth").error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
