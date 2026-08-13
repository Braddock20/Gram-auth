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
    host: str
    port: int
    log_level: str

def load_settings():
    username = os.getenv("INSTAGRAM_USERNAME", "").strip()
    password = os.getenv("INSTAGRAM_PASSWORD", "")
    raw = os.getenv("INSTAGRAM_SESSION_FILE", "sessions/instagram.json")
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    if not username or not password:
        raise RuntimeError("INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set.")
    return Settings(username, password, path,
                    os.getenv("HOST", "0.0.0.0"),
                    int(os.getenv("PORT", "10000")),
                    os.getenv("LOG_LEVEL", "INFO").upper())
