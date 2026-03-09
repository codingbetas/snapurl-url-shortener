SnapURL - URL Shortener

A modern full-stack URL shortener built with FastAPI and Next.js.
SnapURL allows users to create short links, track clicks, and view analytics.

Features

Generate short URLs

Custom aliases for links

Link expiration support

Click tracking

IP logging

URL statistics dashboard

Tech Stack
Backend

FastAPI

SQLAlchemy

SQLite

Frontend

Next.js

React

Tailwind CSS

Project Structure
snapurl-url-shortener
│
├── backend
│   ├── app
│   └── requirements.txt
│
├── frontend
│   ├── app
│   ├── components
│   └── package.json
│
└── README.md
Running the Project Locally
1️⃣ Run Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

Backend runs on:

http://localhost:8000
2️⃣ Run Frontend
cd frontend
npm install
npm run dev

Frontend runs on:

http://localhost:3000
Example
Original URL
https://example.com/very-long-link

Short URL
http://localhost:8000/abc123
Future Improvements

User authentication

Custom domains

QR code generation

Advanced analytics

