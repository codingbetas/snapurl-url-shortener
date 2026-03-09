# SnapURL - URL Shortener 
# SnapURL - URL Shortener

A modern URL shortener built with FastAPI and Next.js.

## Features

- Generate short URLs
- Custom aliases
- Link expiration
- Click tracking
- IP logging
- URL statistics

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite

### Frontend
- Next.js
- React
- TailwindCSS

## Run Backend

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

## Run Frontend

cd frontend
npm install
npm run dev