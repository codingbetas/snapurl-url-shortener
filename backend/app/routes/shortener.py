from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
import os
import secrets
import string
from datetime import datetime, timedelta, timezone
import redis

# NEW imports for fastapi-limiter 0.2.0
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Rate, Limiter

from app.schemas import URLCreate, URLResponse
from app.database import get_db
from app import models

router = APIRouter()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CODE_ALPHABET = string.ascii_letters + string.digits

# We keep Redis for CACHING (this is separate from rate limiting)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, protocol=2)

def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))

# NEW: Create a Limiter object for 5 requests per 60 seconds
limiter = Limiter(Rate(5, Duration.MINUTE))

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
        "ip_address": url.ip_address,
    }

@router.get("/{short_code}")
def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):
    # 1. CHECK REDIS CACHE FIRST
    cached_url = redis_client.get(f"url:{short_code}")
    if cached_url:
        print(f"⚡ CACHE HIT for {short_code}")
        return RedirectResponse(url=cached_url)

    # 2. IF NOT IN CACHE, CHECK DATABASE
    print(f"🐢 CACHE MISS for {short_code}. Hitting Database...")
    url = db.query(models.URL).filter(models.URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="Short code not found")

    now = datetime.now(timezone.utc)
    if url.expires_at:
        expires_at = url.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if now > expires_at:
            raise HTTPException(status_code=410, detail="Link expired")

    # 3. SAVE TO REDIS CACHE
    redis_client.setex(f"url:{short_code}", 3600, url.original_url)

    # 4. UPDATE CLICKS IN DB
    ip = request.client.host if request.client else None
    db.execute(
        update(models.URL)
        .where(models.URL.id == url.id)
        .values(clicks=models.URL.clicks + 1, ip_address=ip)
    )
    db.commit()

    return RedirectResponse(url=url.original_url)


# NEW: Use the limiter object here
@router.post("/shorten", response_model=URLResponse, status_code=201, dependencies=[Depends(RateLimiter(limiter))])
def create_short_url(url: URLCreate, db: Session = Depends(get_db)):
    expires_at = None
    if url.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=url.expires_in_days)

    if url.custom_code:
        new_url = models.URL(
            original_url=str(url.original_url),
            short_code=url.custom_code,
            expires_at=expires_at,
        )
        db.add(new_url)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Short code already exists")
        db.refresh(new_url)
    else:
        for _ in range(5):
            new_url = models.URL(
                original_url=str(url.original_url),
                short_code=generate_code(),
                expires_at=expires_at,
            )
            db.add(new_url)
            try:
                db.commit()
                db.refresh(new_url)
                break
            except IntegrityError:
                db.rollback()
                continue
        else:
            raise HTTPException(status_code=500, detail="Could not generate unique code")

    return {
        "short_code": new_url.short_code,
        "short_url": f"{BASE_URL}/{new_url.short_code}",
    }