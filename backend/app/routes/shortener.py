from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import random
import string
from datetime import datetime, timedelta

from app.schemas import URLCreate, URLResponse
from app.database import SessionLocal
from app import models

router = APIRouter()


# -----------------------------
# DB Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Stats Endpoint
# -----------------------------
@router.get("/stats/{short_code}")
def get_stats(short_code: str, db: Session = Depends(get_db)):
    url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short code not found")

    return {
        "original_url": url.original_url,
        "clicks": url.clicks,
        "created_at": url.created_at,
        "expires_at": url.expires_at,
        "ip_address": url.ip_address
    }


# -----------------------------
# Redirect Endpoint
# -----------------------------
@router.get("/{short_code}")
def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):

    url = db.query(models.URL).filter(models.URL.short_code == short_code).first()

    if not url:
        raise HTTPException(status_code=404, detail="Short code not found")

    # Expiration check
    if url.expires_at and datetime.utcnow() > url.expires_at:
        raise HTTPException(status_code=410, detail="Link expired")

    # Track IP
    ip = request.client.host
    url.ip_address = ip

    # Increase click count
    url.clicks += 1
    db.commit()

    return RedirectResponse(url=url.original_url)


# -----------------------------
# Generate Unique Code
# -----------------------------
def generate_code(db: Session, length: int = 6):
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        existing = db.query(models.URL).filter(models.URL.short_code == code).first()
        if not existing:
            return code


# -----------------------------
# Create Short URL
# -----------------------------
@router.post("/shorten", response_model=URLResponse, status_code=201)
def create_short_url(url: URLCreate, db: Session = Depends(get_db)):

    if url.custom_code:
        short_code = url.custom_code
    else:
        short_code = generate_code(db)

    existing = db.query(models.URL).filter(models.URL.short_code == short_code).first()

    if existing:
        raise HTTPException(status_code=400, detail="Short code already exists")

    expires_at = None

    if url.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=url.expires_in_days)

    new_url = models.URL(
        original_url=str(url.original_url),
        short_code=short_code,
        expires_at=expires_at
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    BASE_URL = "https://snapurl-url-shortener-1.onrender.com"

    return {
    "short_code": new_url.short_code,
    "short_url": f"{BASE_URL}/{new_url.short_code}"
    }