from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
import os
import secrets
import string
from datetime import datetime, timedelta, timezone

from app.schemas import URLCreate, URLResponse
from app.database import get_db
from app import models

router = APIRouter()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CODE_ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


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

    ip = request.client.host if request.client else None
    db.execute(
        update(models.URL)
        .where(models.URL.id == url.id)
        .values(clicks=models.URL.clicks + 1, ip_address=ip)
    )
    db.commit()

    return RedirectResponse(url=url.original_url)


@router.post("/shorten", response_model=URLResponse, status_code=201)
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