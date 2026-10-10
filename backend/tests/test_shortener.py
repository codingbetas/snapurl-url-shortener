import concurrent.futures
from datetime import datetime, timedelta, timezone

from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

from app import models


def test_shorten_creates_url(client):
    response = client.post(
        "/shorten",
        json={"original_url": "https://example.com/very-long-url"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert data["short_url"].endswith(data["short_code"])


def test_custom_code(client):
    response = client.post(
        "/shorten",
        json={
            "original_url": "https://example.com/page",
            "custom_code": "my-portfolio",
        },
    )
    assert response.status_code == 201
    assert response.json()["short_code"] == "my-portfolio"


def test_duplicate_custom_code_rejected(client):
    client.post(
        "/shorten",
        json={
            "original_url": "https://example.com/a",
            "custom_code": "dup",
        },
    )
    response = client.post(
        "/shorten",
        json={
            "original_url": "https://example.com/b",
            "custom_code": "dup",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_redirect_increments_clicks(client):
    create = client.post(
        "/shorten",
        json={"original_url": "https://example.com/click-test"},
    )
    code = create.json()["short_code"]

    r1 = client.get(f"/{code}", follow_redirects=False)
    assert r1.status_code in (302, 307)

    stats = client.get(f"/stats/{code}")
    assert stats.status_code == 200
    assert stats.json()["clicks"] == 1

    client.get(f"/{code}", follow_redirects=False)
    stats = client.get(f"/stats/{code}")
    assert stats.json()["clicks"] == 2


def test_concurrent_increments_are_atomic(engine, client):
    """
    Proves that concurrent increments to the clicks counter do not
    lose updates.

    We bypass the FastAPI TestClient (which shares one session across
    threads) and open N independent SQLAlchemy sessions, each running
    the same atomic UPDATE. The final count must equal N.

    This is exactly what the production code does per HTTP request:
    each request gets its own session, then runs
    `UPDATE urls SET clicks = clicks + 1`.
    """
    create = client.post(
        "/shorten",
        json={"original_url": "https://example.com/atomic"},
    )
    code = create.json()["short_code"]

    SessionForThreads = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    with SessionForThreads() as s:
        url = s.query(models.URL).filter(
            models.URL.short_code == code
        ).first()
        url_id = url.id

    def increment():
        session = SessionForThreads()
        try:
            session.execute(
                update(models.URL)
                .where(models.URL.id == url_id)
                .values(clicks=models.URL.clicks + 1)
            )
            session.commit()
        finally:
            session.close()

    # 20 threads: enough to make the race window likely, few enough to keep
    # the test fast and stable across CI environments. The atomic SQL
    # increment is correct for any N; this test verifies the property.
    N = 20

    with concurrent.futures.ThreadPoolExecutor(max_workers=N) as ex:
        futures = [ex.submit(increment) for _ in range(N)]
        for f in futures:
            f.result()

    with SessionForThreads() as s:
        url = s.query(models.URL).filter(models.URL.id == url_id).first()
        assert url.clicks == N, f"Expected {N}, got {url.clicks}"


def test_unknown_code_returns_404(client):
    response = client.get("/nonexistent-code")
    assert response.status_code == 404


def test_expired_link_returns_410(client, db_session):
    create = client.post(
        "/shorten",
        json={"original_url": "https://example.com/expired"},
    )
    code = create.json()["short_code"]

    url = db_session.query(models.URL).filter(models.URL.short_code == code).first()
    url.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db_session.commit()

    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 410