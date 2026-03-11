🔗 SnapURL – High-Performance URL Shortener

SnapURL is a modern full-stack URL shortening platform designed for speed, reliability, and simplicity.
It converts long, cumbersome URLs into short, manageable links while providing analytics, expiration control, and custom aliases.

The project demonstrates a production-style architecture with a decoupled frontend and backend deployed on separate platforms.

🚀 Live Demo

<img width="544" height="657" alt="Image" src="https://github.com/user-attachments/assets/c3449585-090d-49cf-91c4-70898ded78c8" />

Frontend Application

https://snapurl-url-shortener.vercel.app

Backend API Documentation

https://snapurl-url-shortener-1.onrender.com/docs

✨ Key Features
🔗 Smart URL Shortening

Instantly convert long URLs into compact links using a unique short code generator.

🏷 Custom Aliases

Create personalized or branded links.

Example:

/my-portfolio
/github
/docs
⏳ Link Expiration

Set expiration dates for temporary links.

📊 Real-time Analytics

Track link usage with:

Click count

Creation time

Visitor IP logging

🖥 Interactive Dashboard

Modern UI inspired by glassmorphism design, allowing users to:

generate short links

copy links instantly

view statistics

🛠 Tech Stack
Backend

FastAPI — high-performance async API framework

SQLAlchemy — database ORM layer

SQLite — lightweight relational database

Frontend

Next.js — modern React-based framework

React — component-based UI

Tailwind CSS — responsive styling

Deployment

Frontend hosted on Vercel

Backend hosted on Render

This architecture separates the UI and API layers, allowing the backend to serve multiple clients such as web, mobile, or CLI applications.

🏗 Project Architecture

The project follows a decoupled client-server architecture.

snapurl-url-shortener
│
├── backend
│   ├── app
│   │   ├── main.py          # FastAPI application entry
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Request/response schemas
│   │   ├── database.py      # Database configuration
│   │   └── routes           # API endpoints
│   │       ├── shortener.py
│   │      
│   │    
│   │
│   └── requirements.txt
│
├── frontend
│   ├── app                  # Next.js app router
│   ├── components           # Reusable UI components
│   ├── public               # Static assets
│   └── package.json
│
└── README.md
⚙ Running the Project Locally
1️⃣ Backend Setup

Navigate to the backend directory:

cd backend

Install dependencies:

pip install -r requirements.txt

Start the FastAPI server:

uvicorn app.main:app --reload

Backend runs at:

http://localhost:8000

API documentation:

http://localhost:8000/docs
2️⃣ Frontend Setup

Navigate to the frontend directory:

cd frontend

Install dependencies:

npm install

Start development server:

npm run dev

Frontend runs at:

http://localhost:3000
📌 Example

Original URL

https://example.com/very-long-link

Generated Short URL

https://snapurl-url-shortener-1.onrender.com/abc123

Opening the short link redirects the user to the original destination.

📈 Future Roadmap

Planned improvements for SnapURL:

User authentication with JWT

Custom domain support

QR code generation for links

Rate limiting and security enhancements

Advanced analytics (device, location, browser)

Link management dashboard

👤 Author

Himanshu Rathod

GitHub:
https://github.com/codingbetas

LinkedIn:
https://www.linkedin.com/in/himanshu-rathod-5815991bb/

This project is open-source and available under the MIT License.

