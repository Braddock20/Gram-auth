from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

@dataclass(frozen=True)
class Settings:
    username: str
    password: str
    session_file: Path
    log_level: str = "INFO"

def load_settings() -> Settings:
    username = os.getenv("INSTAGRAM_USERNAME", "").strip()
    password = os.getenv("INSTAGRAM_PASSWORD", "")
    session_file = Path(os.getenv(
        "INSTAGRAM_SESSION_FILE", "sessions/instagram.json"
    ))
    if not session_file.is_absolute():
        session_file = ROOT / session_file

    if not username or not password:
        raise RuntimeError(
            "Missing INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD in .env"
        )

    return Settings(
        username=username,
        password=password,
        session_file=session_file,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
