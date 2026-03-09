from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI 
from app.routes import shortener
from app.database import engine
from app import models

app = FastAPI(title="Url-shortener")

models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {
        "status" : "ok",
        "server" : "URL Shortener is running"
    }
    
app.include_router(shortener.router)