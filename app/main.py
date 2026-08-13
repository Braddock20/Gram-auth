import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .config import load_settings
from .auth import AuthManager

s = load_settings()
logging.basicConfig(level=getattr(logging, s.log_level, logging.INFO),
                    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI(title="Instagram Authentication Service", version="1.0.0")
auth = AuthManager(s.username, s.password, s.session_file)

class VerifyRequest(BaseModel):
    code: str = Field(min_length=4, max_length=32)

@app.get("/")
def root():
    return {"ok": True, "service": "instagram-auth", "state": auth.status()["state"]}

@app.get("/health")
def health():
    return {"ok": True, "service": "instagram-auth"}

@app.get("/auth/status")
def status():
    return auth.status()

@app.post("/auth/login")
def login():
    result = auth.login()
    if result["state"] == "RATE_LIMITED":
        raise HTTPException(429, result)
    return result

@app.post("/auth/verify")
def verify(body: VerifyRequest):
    result = auth.login(body.code.strip())
    if result["state"] == "RATE_LIMITED":
        raise HTTPException(429, result)
    return result

@app.post("/auth/logout")
def logout():
    auth.logout()
    return auth.status()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=s.host, port=s.port)
